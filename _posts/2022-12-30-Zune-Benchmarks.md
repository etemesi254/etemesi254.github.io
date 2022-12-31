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

[criterion]:https://github.com/bheisler/criterion.rs
[here]: /assets/criterion/report/index.html
