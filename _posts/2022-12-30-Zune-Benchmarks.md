---
layout: post
title: Zune benchmarks
date: 2022-10-30 07:00:00 -0000
categories: optimizations
tags: rust
---

This contains a permalink to the zune library benchmarks, reports provided by
[criterion]

Currently, benchmarks are ran on my machine, but will hopefully soon move to a cloud provider


## Machine Specs

| Feature            | Value                                  |
|--------------------|----------------------------------------|
| Model name         | AMD Ryzen 5 4500U with Radeon Graphics |
| CPU family         | 23                                     |
| Model              | 96                                     |
| Thread(s) per core | 1                                      |
| Core(s) per socket | 6                                      |
| L1d                | 192 KiB (6 instances)                  |
| L1i                | 192 KiB (6 instances)                  |
| L2                 | 3 MiB (6 instances)                    |
| L3                 | 8 MiB (2 instances)                    |

## Benchmarks
[here]

## Last Update Time
13th February 2023

## Replicating
The command to create this is as follows

Tested on Linux
```sh
# Clone the repo
git clone https://github.com/etemesi254/zune-image
# cd into the repo
cd ./zune-image
# compile and run benchmark
RUSTFLAGS='-C target-cpu=native' cargo bench --workspace

```
We run on the highest optimization possible on one's computer, hence the `RUSTFLAGS` declaration to ensure the codecs are compiled with the sweetest, most cool CPU instructions to run in your machine.

## Disclaimer
The purpose of this is to show how decoders fare up against one another.

The author does say that (currently) all `zune-` decoders are written by him,hence he may be biased on outputs,

If you feel such may be the case, feel free to file an issue, or a pull request implementing the correct benchmarks

[criterion]:https://github.com/bheisler/criterion.rs
[here]: /assets/criterion/report/index.html
