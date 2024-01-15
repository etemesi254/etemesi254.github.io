---
layout: post
title: The architecture of Pixly - A simple image editor in Kotlin + Rust
date: 2024-01-15 07:00:00 -0000
categories: architecture kotlin  kotlin multiplatform rust
tags: kotlin architecture
---

![Main Window](/assets/imgs/pixly/main_screen.png)

Photo  of tree by <a href="https://unsplash.com/@colinwatts?utm_content=creditCopyText&utm_medium=referral&utm_source=unsplash">Colin Watts</a> on <a href="https://unsplash.com/photos/a-dead-tree-in-the-middle-of-a-desert-RO5ZTQQmePc?utm_content=creditCopyText&utm_medium=referral&utm_source=unsplash">Unsplash</a>

Pixly is an image editor for Android and Desktop platforms that uses Compose and Rust to achieve a simple image editing experience.

It provides a GUI/Frontend to my other toy project [zune-image], a high perfomance library for decoding processing and encoding various image formats.

It has the features you'd expect from a simple editor, like history, image filters, thumbnails, image operations, e.t.c and some nice to haves like double pane layout and directory navigator.

Feature wise, it is definitely not there, but it has some nice properties I thought would be nice putting down somewhere, and this blog does exactly that, going into a high level overview of the architecture and the low level bits like getting pixels to screen and keeping memory usage low.

## Why

I wanted a small Lightroom alternative that works in Linux, that's all.

## High level architecture

### Application logic

Application logic is stored in `commonMain` which means it's shared between the Desktop and Android endpoints.

Most logic is stored in `AppContext`, with functions manipulating what they need and widgets reacting to it.

Since there is no full one-to-one mapping of widgets and functionality between Android and Desktop, some functions/classes are represented as interfaces with each platform creating a concrete class that implements that interface.

The most common interfaces implemented include [`ProtectedBitmapInterface`](https://github.com/etemesi254/Pixly/blob/main/composeApp/src/commonMain/kotlin/ProtectedBitmapInterface.kt) which is just a platform specific image bitmap and a mutex that protects it from dangerous multithreaded accesses that may cause invalidations and segfaults and [`ZilBitmapInterface`](https://github.com/etemesi254/Pixly/blob/main/composeApp/src/commonMain/kotlin/ZilBitmapInterface.kt) that unifies the image operations that are implemented.

Most of the app logic lies in [AppContext.kt](https://github.com/etemesi254/Pixly/blob/main/composeApp/src/commonMain/kotlin/AppContext.kt)

### Image manipulation

While Kotlin/Java is platform agnostic, Rust doesn't have that as it is a compiled language, this means that `zune-image` has to be built for multiple endpoints/backends, the backends currently supported are  `linux-x86-64`, `windows-x86-64-gnu` for desktop platforms and `aarch64-linux-android`,`armv7-linux-androideabi` and`i686-linux-android`  for android platforms.

The overall image architecture looks like the following

![Overall architecture](/assets/imgs/pixly/overall_architecture.png)

The reason to have different  platform specific interface implementors is because we have to do some 'low-level' manipulation in both Desktop and Android, to get pixels to the screen. Compose when targeting Android uses the Android's default [Bitmap](https://developer.android.com/reference/android/graphics/Bitmap) class for handling images while the desktop implements it's own [SkiaBackedImageBitmap](https://jetbrains.github.io/skiko/skiko/org.jetbrains.skia/-bitmap/index.html?query=class%20Bitmap%20:%20Managed,%20IHasImageInfo) each with a different API but all of can be converted to an  `ImageBitmap` interface which encapsulates both classes to a single API surface.

Both of these have separate apis, e.g the desktop implementation can read from `ByteArray` via [Bitmap.installPixels](https://jetbrains.github.io/skiko/skiko/org.jetbrains.skia/-bitmap/index.html?query=class%20Bitmap%20:%20Managed,%20IHasImageInfo#-58173881%2FFunctions%2F788909594) whereas the Android can read from `ByteBuffer` via [Bitmap.copyPixelsFromBuffer](https://developer.android.com/reference/android/graphics/Bitmap#copyPixelsFromBuffer(java.nio.Buffer))

### Widgets

As the project aimed to be multiplatform, this meant that there was a limit as to what can be considered platform agnostic, a simple thing such as how Android and Desktop compose handle svg/xml means that any path that was setting up such needed to be re-implemented in both platforms and non-trivial things such as color representation meant the image bits had to be repeated for both platforms.

If a widget or method qualified as platform agnostic(by qualification we mean it didn't cause compile errors when compiled for both Android and Desktop),it was stored in `commonMain` , if not, it was placed in  specific platform folder.

## Getting into the bits

With the high overview architecture explained, we can spend some more time looking into the low level details that actually make an image operation succeed and the nuances needed to make it work.

### JNI

Java communicates with other C like languages via the JNI, a [Foreign Function Interface (FFI)](https://en.wikipedia.org/wiki/Foreign_function_interface) the JVM understands. 

This means for us to implement the bridge between the JVM and Rust, we must write a small shill layer to handle that [^1]

A sample code for Kotlin for jni looks like

```kotlin

class ZilImageJni  {
    /// Image pointer, points to the memory that contains the Rust image struct
    private var imagePtr:Long = createImagePtrNative()
    
    /// Create and load an image pointed to by `file`
    constructor(file: String) {
        loadImageNative(imagePtr, file)
    }
    private external fun createImagePtrNative(): Long

    // ... other methods
}
```
The file that contains the JNI from kotlin side is found in [commonMain/ZilImageJni.kt](https://github.com/etemesi254/Pixly/blob/main/composeApp/src/commonMain/kotlin/ZilImageJni.kt)

A sample Rust code looks like

```rust
/// Create an image and return the pointer to that image in memory
#[no_mangle]
pub extern "system" fn Java_ZilImageJni_createImagePtrNative(_env: JNIEnv, _class: JClass) -> jlong {
    let image = Image::new(vec![], BitDepth::Unknown, 1, 1, ColorSpace::Unknown);

    let c = Box::new(image);
    // convert it to a pointer
    Box::into_raw(c) as jlong
}
```

The name and order of arguments matter, as it should follow [JNI specifications](https://docs.oracle.com/en/java/javase/17/docs/specs/jni/design.html). If JVM doesn't find a method expected, the application crashes with an [`UnsatisfiedLinkError`](https://docs.oracle.com/javase/8/docs/api/java/lang/UnsatisfiedLinkError.html)

The rust file containing JNI functions can be found in [rust/src/lib.rs](https://github.com/etemesi254/Pixly/blob/main/rust/src/lib.rs)

### Initial preprocessing

Images come in different types, if we are to consider bit-depth and colorspace but the one thing we want to unify is how they are shown. Compose and Android use 32 bit ARGB where each image pixel is represented as a packed 32 bit integer, i.e `R` occupies 8 bits, `G` 8 bits and so do `B` and `A` they are then bit packed into one integer and that is represents a color.

So this means `zune-image` must obey the same layout, so on image loading, we convert the pixels to BGRA/RGBA depending on platform(we'll explain this later) and then convert depth to 8 bits per image color.

```kotlin
class ZilBitmap(inner: ZilImageInterface){

    override fun prepareNewFile(bitmap: ProtectedBitmapInterface) {
        // convert depth to u8
        inner.convertDepth(ZilDepth.U8);
        // convert colorspace to BGRA
        inner.convertColorspace(ZilColorspace.BGRA)
        // ...
    }
}
```

### Getting Memory from Rust to the screen.

`zune-image` does most of the heavy lifting when it comes to processing, so when you press any slider, it needs to manipulate pixels and send those pixels back to kotlin for them to be rendered by skia.

`zune-image` represents images in planar format  but Compose/Skia wants data in interleaved `ARGB`, so we have to convert planar channels into ARGB before we send to skia.
![Animation of Planar to RGB](/assets/imgs/pixly/zune_image_to_kotlin.gif)

An interesting thing is that skia uses ARGB in little endian, with 32 bit number to represent a pixel, when processing images, we represent each pixel with a byte (assuming a bit depth of 8), so that means in memory were we to pack ARGB into an integer, we would have the most significant bit as `A` and the least significant bit as `B`. 

But such normal packing is what is expected in big-endian architectures, little endian has the least significant bit in the left and most significant in the right, it would appear backwards when visualized, meaning were we to actually convert to ARGB, we would be showing wrong color mixes. 

Well the solution is to convert it to `BGRA`, we mentioned little endian looks backwards when visualized, and if we are to arrange `ARGB` backwards, we would have `BGRA`, so this is the colorspace that shows the right colors on the screen.  

### Keeping memory usage low

![A 5184 by  3456 image opened in pixly, there is a yellow hightlight](/assets/imgs/pixly/memory_usage.png)

Images can get very big very quickly, the above picture shows a 5184 x 3456 image using 68 Mb for it's in memory pixel cache (highlighted in yellow box) whereas the size in disk is just 2.3 mb( highlighted in purple box)

It gets more complicated

- `zune-image` needs to store it's own copy of pixels
- skia also stores pixels in its own native memory
- We need a way to transfer bytes from zune-image to skia, which means we need a big enough buffer to hold all image pixels.
- Jvm doesn't allow one to acess `ByteArray` from native code, only directly allocated buffers using `ByteBuffer` can be accessed in native meethods so we need a `ByteBuffer` that can hold image pixels
  
Each one of the above is an allocation as big enough as the image loaded, which means we need 4x the image storage to show it to screen.

Furthermore, adding history rollbacks, especially on operations where we have to create a copy(e.g when implementing undo for a blur opetation), we may end up consuming a lot of memory if we aren't careful.

While there are some allocations we can't prevent, we can ensure those we control don't devolve into anarchy by reusing allocations where possible.

#### Saving on bytebuffer memory

One place we can optimize is the buffers used for writing pixels from Rust JNI to something the Jvm understands, a naive solution would be to create a bufer and write to it on every invocation that needs to see pixels, this would go very bad very quickly, as it would create short lived but very big arrays putting pressure on the operating system and the JVM when it has to do garbage collection.

To solve this, we can create one big array and share it with various operations that manipulate the image in any way but ensuring we protect it via a mutex to prevent data races and pointer invalidations.

The name aptly given to this is the [`SharedBufer`](https://github.com/etemesi254/Pixly/blob/6012fdafc5d2b9a7c76934ac6d7559c804ab07d1/composeApp/src/commonMain/kotlin/AppContext.kt#L25) which literally represents a shared buffer used by various image operations.

An operation can lock the `SharedBuffer`'s mutex and then it's free to allocate, resize,deallocate or replace the buffers present. This helps us only have one buffer even when multiple images are opened or after multiple operations have been executed, saving us memory.

#### Reusing Bitmap allocations when possible

Another area we can optimize is by carefully considering how skia image works which processes allocate and using that knowledge to reduce allocations as much as possible.

On desktop, skia image contains `allocPixels` that allocates pixel memory, we can optimize the function that calls this to only change if the storage doesn't match i.e the function that does that in desktop is

```kotlin
class ZilBitmap {
    private fun allocBuffer(bitmap: Bitmap) {

        // check if buffer would fit the new type
        // i.e do not pre-allocate
        val infoSize = image.height * image.width
        val imageSize = image.height().toInt() * image.width().toInt();

        info = ImageInfo.makeN32(
                image.width().toInt(),
                image.height().toInt(),
                ColorAlphaType.UNPREMUL,
                ColorSpace.sRGB)

        bitmap.setImageInfo(info)

        if (infoSize != imageSize) {
            assert(bitmap.allocPixels(info))
        }
    }
}
```

This function does something interesting, it modifies image information per invocation, but only allocates the pixel if info size varies from the new image size.
This makes sense when considering operations like `brighten` don't modify pixel size but also means operations like `rotate` and `transpose` which just change dimensions won't cause a reallocation,we only re-allocate when we have to.

### Hinting the GC that it should probalby run

The Java garbage collector takes care of memory for the programmer and runs occasionaly to free resources with no references.

Image programs use a lot of data when dealing with history, for there are operations we need to store a whole copy of the image, but sometimes these are short lived.

An example is if you change the slider for contrast and then undo it, for those chain of operations, we have to create a copy of the image, apply contrast operation, render to screen, and then remove the copy of the image from our history, this means that the memory the image used should be freed, but when this occurs is non-deterministic.

But we know where we expect memory pressure, when we add an element to history, and when we remove an element from it, so on such places, we can simply hint the Garbage collector telling it to free memory.

Java provides `System.gc()` which is a hint to the JVM to carry out grabage collection, and we insert this into the functions that deal with history.

Here, we trade CPU cycles to get a better memory usage, how beneficial that is, it's up for debate

## Threads, mutexes and preventing segfaults

When an image operation like `blur` or `exposure` is requested, the operation is launched on an IO thread to prevent blocking of the UI thread.

Kotlin has powerful coroutines, which depending on configuration, dispatch requests to the main UI thread, blocking any other work or what it calls IO threads which is a threadpool maintained by the Jvm where calls using `Dispatchers.IO` are ran on.

While it is obvious that we would have image operations running on I/O thread, we reach a dangerous path when we mix it with the memory optimizations mentioned above.

Specifically assume we are running a CPU intensive operation like `median blur`, while it's running, the user also increases contrast, the `contrast` runs on a separate thread and finishes before the initial `median blur`, then it updates the canvas and then finally `median blur` finishes and updates the canvas.What will happen is that the canvas will contain `median blur` changes but not `contrast` changes, that introduces an inconsitency in operations.

But such is a mere annoyance, the real problem comes when we think about bitmaps, specifically we only use one bitmap to keep memory low, the address of the  pixel location of the bitmap isn't static and may be invalidated e.g when we change an image, so the problem may be that the UI thread is drawing just finished pixels and it's still in the step of reading them from memory and a new operation invalidates that memory address leaving it with a dangling pointer,or what `C` people call use-after-free.

If you are lucky, skia will complain with `FailedToMakeBitmap` `ptr=null` and if you spent enough time in low level languages like `C/C++`, you'd understand skia found a null pointer, if you aren't the application just segfaults, and you get a nice  memory and thread dump to tell you you really messed up.

The fix for such things is to introduce mutexes, mutexes help protect shared resources you don't want people peeking into and grabbing it from you, this is the reason for the existence of `ProtectedBitmapInterface`, it is a bitmap that is protected by a mutex, the interface is very simple

```kotlin
interface ProtectedBitmapInterface {

    fun asImageBitmap(): ImageBitmap

    fun mutex(): Mutex

}
```

The usage is that you are to lock the mutex returned by the `mutex` before you read the image via the `asImageBitmap` , this helps us ensure that there is always one reader or writer of this class at a time, and if correctly used, no two threads should manipulate the same resource at the same time.

## Conclusion

The challenge was a fun one, with a lot learnt in how to mkake two systems communicate with each other correctly, the app is definitely not production ready yet, a lot of bugs still exist and the latency between the image operations to the screen make for a noticeable lag not experienced in other professional image editors like Lightroom.

---

[^1]: That may change soon, see [Project Panama](https://openjdk.org/projects/panama/)


[zune-image]: https://github.com/etemesi254/zune-image