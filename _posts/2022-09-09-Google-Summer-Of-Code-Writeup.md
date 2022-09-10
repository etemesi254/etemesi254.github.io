---
layout: post
title: Google Summer of Code Writeup - Adding HTJ2K to FFmpeg
date: 2022-09-09 07:00:00 -0000
categories: gsoc-2022
---


> The patch that was submitted to ffmpeg can be viewed  [here](https://patchwork.ffmpeg.org/project/ffmpeg/patch/20220908204953.46737-1-etemesicaleb@gmail.com/)
{:.prompt-tip }
> A working ffmpeg implementation used to produce image samples can be found [here](https://github.com/etemesi254/FFmpeg)
{:.prompt-tip }

The recently concluded Google Summer of Code program saw me participating in adding a high-throughput jpeg2000 decoder for ffmpeg and this is my writeup on experiences gained during that period.

## Background and motivation

Jpeg2000 came out almost two decades ago as a successor to the jpeg standard, it offered better compression, advanced modes, lossy and lossless compression ,scaling, support for images larger than 64K by 64K and other niceties,but all of thess nice features came with a relatively high computational complexity

One of the major computational complexity arose from its use of a context-based arithmetic coder to do entropy coding, while this is superior in terms of compression ratio to other entropy coding styles like Huffman, it suffers heavily while it comes to speed, such a decoder isn't vectorizable and has long dependency chains, uses expensive instructions like division in its decoder(a characteristic of most arithmetic coders) which slow it considerably down in relation to other entropy decoders.

With this in mind, a new specification arose that addresses this shortcoming by providing a drop in entropy coder for jpeg2000 was born, and it is what we call the JPEG2000 Hight Throughput decoder.

It replaces the Arithmetic coder with a simpler block coder that uses bit-packing techniques to efficiently encode the stream, furthermore, it allows vectorizable implementations of the block decoder, already implemented in some open source decoders( [openJPH](https://github.com/aous72/OpenJPH) and [OpenHTJ2K](https://github.com/osamu620/OpenHTJ2K)) which allow even faster decode speeds for those implementations.

To increase adaptability, it is important that more tools support such codestreams, and this was a step in that direction, adding ffmpeg -the swiss army knife for multimedia- to the list of programs supporting HTJ2K allows easier adaptation by the general audience and developers all alike, and an increase in use of jpeg2000 as a codec as a whole.

## Implementation

The implementation in ffmpeg is mainly broken down into two portions,
the main portion being  in `libavcodec/jpeg2000htdec.[h|c]`which hosts the decoder implementation and the other being changes to other files e.g `jpeg2000dec.h` to allow decoding of htj2k images while utilizing the jpeg2000 infrastructure that already exists in ffmpeg(e.g. marker parsing).

## Reasons why I picked this project

1. I find codecs fascinating

2. I love optimizing code

## Results

A test file that contains a high-throughput jpeg2000 codestream can be downloaded below

<a href = "/assets/imgs/gsoc/ht.j2c" downloadable>
Click here to download
</a>

Below, we compare how ffmpeg handled htj2k codestreams before the patch and after

| Before                                                     | After                                                                              |
| ---------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| ![A greyed out image](/assets/imgs/gsoc/ffmpeg_before.jpg) | ![A black image with a white text written `0`](/assets/imgs/gsoc/ffmpeg_after.jpg) |

The decoder can also decode complicated ht-codestreams such as the one below

<a href = "/assets/imgs/gsoc/meridian.ht.j2c" downloadable>
Click here to download
</a>

To

![Man wearing a spandex staring into space beyond the camera. Light is streaming through window panes illuminating hisleft hand, an old clock is behind him reading 4:33 pm](/assets/imgs/gsoc/meridian.ht.jpg)

## Highlights

Working on this project was fun and definitely eye-opening, I did come out better than I was initially, a better devolper, better collaborator, and a better person all-round.

It was a project I could not shove down the drain once I got bored and I appreciate that this was one of the projects I saw to completion

Some things I got out from this program was

1. Advanced `git` usage, `git` is way more than `clone`,`commit`,`add` and `push`. It was interesting and eye-opening using features like `format-patch` and `send-email`.
2. Safe C, forever testing all C code using valgrind now.
3. Collaborative work, how it feels to work in a distributed team where someone is changing something, and how to keep development moving in such cases
4. Forums and mailing lists, joined some mailing lists that seem to interest me

## Challenges

Any sufficiently complicated system has it's own complicated challenges, and ffmpeg is not an exception.

I spent a lot of time trying to understand the current jpeg2000 decoder present in ffmpeg as it is with most systems, complex code tends to be understood by those who wrote it, while the high coding standards were of help(i.e useful variable names), it didn't help to have

There was also a lot of expected knowledge one needed to know in order to write code,for ffmpeg, e.g. a statement as vague as keeping changes arising from moving code separate from changes separate from functional code usually goes over ones head until reviewing time, when experienced people point that out(e.g [Michael Niedermayer pointing out some fixes for my patch](http://ffmpeg.org/pipermail/ffmpeg-devel/2022-September/301211.html))

## Conclusion

Participating in GSOC'22 was an interesting challenge that I enjoyed, and which I found was a good footing to start on as I continue in my programmers' journey and foray into other things.

It also imbued me with a deep appreciation of open source, as it powers the world, from the famous Linux kernel to the common jpeg decoder that made all images for this site possible, and it is a great honour to be a part of such a team.

To more opensource.


## Additional work

While the decoder is complete, it  still has to pass the scrutiny of ffmpeg standards, which involve other developers reviewing the code, and suggesting fixes/improvements.

The other agenda involves various decoder speed optimizations that didn't make it to the decoder at the submission time.

These optimizations have to undergo rigorous testings to ensure they provide bit-identical output to the currently working decoder and are safe and additional benchmarks to justify the optimizations.

Currently, some of these optimizations are present in the [htj2k-optims](https://github.com/etemesi254/ffmpeg-ht/compare/htj2k...htj2k-optims) branch in my ffmpeg clone.


## Acknowledgments.

Special thanks to Pierre-A. Lemieux who was my mentor during the gsoc period, his expertise in debugging and git proved invaluable during this period.

Thanks to Osamu Watanabe for releasing his own implementation of a HT decoder, @ [https://github.com/osamu620/OpenHTJ2K](https://github.com/osamu620/OpenHTJ2K) from which my implementation heavily borrows from and who took his time to answer some of my questions during development and was generous enough to provide image samples.

Thanks to Aous T. Naman who made time to answer my questions both in the discord chat and in video meetings, your input was valuable.

And thanks to everyone who made this possible.

## References

1. HTJ2K whitepaper: [https://ds.jpeg.org/whitepapers/jpeg-htj2k-whitepaper.pdf](https://ds.jpeg.org/whitepapers/jpeg-htj2k-whitepaper.pdf)
2. HTJ2k specification [https://www.itu.int/rec/T-REC-T.814-201906-I/en](https://www.itu.int/rec/T-REC-T.814-201906-I/en)
3. HTJ2K Open-Source Implementations
   - [https://gitlab.com/wg1/htj2k-rs/](https://gitlab.com/wg1/htj2k-rs/) - Reference implementation
   - [https://github.com/aous72/OpenJPH](https://github.com/aous72/OpenJPH)
   - [https://github.com/osamu620/OpenHTJ2K](https://github.com/osamu620/OpenHTJ2K)

4. HTJ2K resources [https://github.com/chafey/HTJ2KResources](https://github.com/chafey/HTJ2KResources)
