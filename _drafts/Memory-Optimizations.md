---
layout: post
title: On the underlooked perfomance of less memory allocations
categories: performance
tags: performance, C, Rust
---

In the world of perfomance optimizations, one of the most underlooked optimizations techniques is using less memory, we quickly 


## CASE 1: STB JPEG

stb image is a really great library used by a lot of developers when you want a simple image loader as a header file.

It contains some really nice image decoders with some exceptional perfomance for its size, but do note that the library doesn't aim to be 100% performance oriented, this is just something I came by


The library can decode jpeg, and jpegs come in all flavours, a certain number of them require what is commonly known as [chroma-sub-sampling](https://en.wikipedia.org/wiki/Chroma_subsampling), the technique is that you downsample on encoding the image to either half or a quarter of its size and the decoder up-samples it back to original, think of it as a half/quarter resize.  You definitely loose quality but it saves big on size since you encode way less pixels.

Now decoding the pixels back usually sucks
