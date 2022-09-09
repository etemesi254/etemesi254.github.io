---
layout: post
title: Safe Vs Unsafe, a fighting perspective.
date: 2022-06-19 07:00:00 -0000
categories: programming,rust
tags: safety,programming
---

I have spent an [ungodly]  [amount] [of] [time] looking at [unglodly] [things] in order to either understand how they work or why they work and I've come to the conclusion that the world is held on ductape, and that has never stopped me from messing with ductape.


### When not to use unsafe.

#### 1. When a user is involved.

A lot of programmers, meet are macho programmers, who code until it works and forget about it

##### Introducing the user

My user specifically is `cargo-fuzz`, now fuzzing will find your corner cases, and will overturn your assumptions in ways you cannot think about.

I learnt it the hard way when I fuzzed my amazing jpeg library which I thought to be bug free universally safe and the single most amazing piece of software ever written.

85+ fuzz fixing commits later, the fuzzer is still kicking my ass.

What I'm trying to say is that, the world is not contained in your test cases, your library/application will be hit with everything and anything because such is the minds of users, an unsafe block is the difference between `thread.main panicked at...` and `segmentation fault (core) dumped`, the former is an annoyed user,
the latter may tun out to be `CVE 1212-2022: Out of bounds read in ... causes oom/dos`, pick your poison.

### When to  use unsafe??

<small>TRIGGER WARNING</small>

#### 1. Compilers break
This should probably not be a surprise to anyone given the millions of lines of code that compromise a compiler.

Well how often do compilers break??

Let's play with converting floating point to integers.

##### Converting floats to i128 ints


```rust
/// One line of code
pub fn convert(t:f32)->i128{
    t as i128
}
```
<div style="margin-bottom:4px">
<a href ="https://godbolt.org/z/E3edv7a4a">
<div style="display:flex;align-items: center">
 <img  class ="icon-image" src="https://raw.githubusercontent.com/compiler-explorer/compiler-explorer/main/static/favicon.ico">
 <div style="margin-left: 10px">Godbolt</div>
 </div>
</a>
</div>

And Some C for fun.

```c
__int128_t convert(long double sum){
    return (__int128_t)sum;
}
```
<div style="margin-bottom:4px">
<a href ="https://godbolt.org/z/h1d4PPaPz">
<div style="display:flex;align-items: center">
 <img  class ="icon-image" src="https://raw.githubusercontent.com/compiler-explorer/compiler-explorer/main/static/favicon.ico">
 <div style="margin-left: 10px">Godbolt</div>
 </div>
</a>
</div>

Assembly

GCC, clang.
```nasm
convert:
        sub     rsp, 8
        push    QWORD PTR [rsp+24] ; Increase the stack size??
        push    QWORD PTR [rsp+24]
        call    __fixxfti   ; Call a magic function to do our stuff
        add     rsp, 24     ; Reduce stack ??
        ret
```


And Rust.

Version 1.42

```nasm
example:convert:
        push    rax
        call    qword ptr [rip + __fixdfti@GOTPCREL]
        pop     rcx
        ret
```
Godd damn, we are beating those GCC people, ABI for who????

Then that must mean that on 1.60 we expect shorter code??.



```nasm
.LCPI0_1:
        .quad   0x47dfffffffffffff
example:convert:
        push    rax
        movsd   qword ptr [rsp], xmm0
        call    qword ptr [rip + __fixdfti@GOTPCREL]
        ; So let's convert like GCC, clang and Rust v 1.42

        ; And then CPUs are out of order and stuff, so lets just add
        ; 14 extra instructions that the user won't notice

        xor     ecx, ecx                         ; Set register to zero
        movsd   xmm0, qword ptr [rsp]            ; Move contents of stack to xmm0
        ucomisd xmm0, qword ptr [rip + .LCPI0_0] ; Unordered compare???
        cmovb   rax, rcx                         ; Conditional move what?? rcx is zero, rax is ???
        movabs  rsi, -9223372036854775808        ; -2 ^ 63
        cmovb   rdx, rsi
        ucomisd xmm0, qword ptr [rip + .LCPI0_1]
        movabs  rsi, 9223372036854775807        ; 2 ^ 63
        cmova   rdx, rsi
        mov     rsi, -1                         ; QUITTTT.
        cmova   rax, rsi
        ucomisd xmm0, xmm0
        cmovp   rax, rcx
        cmovp   rdx, rcx
        pop     rcx
        ret
```

I barely understand what happens here, I won't even try to impress anyone with my not so cool assembly annotation skills.

Also,I am not explicitly calling out Rust compiler here, or any compiler for that matter, I barely understand how to write a tokenizer and that compiler solved the P-NP problem of  lifetime issues(and I **love** its error messages), these things happen across the board (go to your favourite compiler and search for regressions in its issue/bugtracker) and sometimes fixes can take long since compiler devs have a life and priorities so sometimes hacks may work.


So a bad hack

```rust
#![feature(core_intrinsics)] // into the night

use std::intrinsics::float_to_int_unchecked;

pub unsafe fn convert_scary(t:f64)->i128{
    // summon demons from hell
    float_to_int_unchecked(t)
}
```

and the Assembly,

```nasm
example:convert_scary:
        push    rax
        call    qword ptr [rip + __fixdfti@GOTPCREL] ; Magic function whooo.
        pop     rcx
        ret
```



#### 2. When performance matters.

I recently became interested in data compression for some reasons I barely understand. Now everyone loves [zstd] and [lz4] because they aren't slow in decompressing, [zstd] can get decompression speeds up to 2 Gb/s while [lz4] does an ungodly 5 Gb/s, which is impressive.

My toy implementation aimed to be somewhere in between there, a little better decompression speeds and a little better compression ratios.

So I came across an issue where I needed  to increase a vectors capacity and length and *overwrite* contents.

I ended up with this,

```rust
let new_len = vec.len()+extra;
vec.reserve_exact(new_len);

unsafe {
    // now we have uninitialized values at the end of
    // the array moving left up to extra
    vec.set_len(new_len);
}
```

<small>Notice I said overwrite, so don't bite me</small>


This should work, and should be safe **if** the other parts of the library adhere to that, but as Sergey Davidoff pointed in this [amazing article about fuzzing](https://shnatsel.medium.com/how-ive-found-vulnerability-in-a-popular-rust-crate-and-you-can-too-3db081a67fb) is that **ifs** don't work.

So I decided to refactor in good faith,
and changed that to this

```rust
let new_len = vec.len()+extra;
vec.resize(new_len,0);
```

 This fills the vector with zeros after extending it, and it was all good, until I benchmarked.

And everything went wrong.

Before

```text
9 - 100000000 bytes -> 53129979 bytes (53.13%)  [1.8822 to 1]   23.60 MB/s 2563.84 MB/s
```

After

```text
9 - 100000000 bytes -> 53129979 bytes (53.13%)  [1.8822 to 1]    21.72 MB/s 1932.84 MB/s.
```

And before you track my home address and come take me outside and tell me why I'm wrong and how `memset` has undergone 30 years of optimizations, please do realize that those speeds are `per second`, 20 Gb/s needs 100 miliseconds to do 2 Gb, sin a hundred miliseconds, we can push 250 more mbs, which matter when you are trying to beat a behemoth that runs at 4.5 Gb/s.
