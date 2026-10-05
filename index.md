---
title: Fast imaging for an GRE sequence
description: GBM8360E midterm project
---

## About this book

The main question behind this book is simple:

How can we make an MRI scan faster without sacrificing image quality?

To explore this question, we focus on a single MRI sequence: the gradient echo (GRE) sequence and explore different ways to accelerate its acquisition.

## The story

Every chapter opens with a short comic, then connects the story to the physics of a real MRI scanner. Indeed, eather than starting with equations, the book follows a small crew of scientists with one mission: get a picture of a flower into a computer, without a digital camera. All they have is a strange machine that turns a painted canvas into a digital image, using the Fourier transform. The catch: painting the canvas takes time. Each scientist has a clever idea to paint faster without losing information. 

:::{figure} images/comics/00-prologue.svg
:label: comicPrologue
:alt: Professor Fourier shows a flower on a pedestal while the crew of scientists cheers.
:::

:::{important} The painting is not the flower
Our scientist do not paint the flower itself. They paint a strange canvas full of stripes, which contains all the information needed by the Fourier transform to rebuild the flower. Physicists call this canvas: the k-space.
:::

Every chapter also contains interactive figures: drag the sliders and watch what happens.

## Contents

1. [](./01-Physics_background.md): the Fourier transform
2. [](./02-gre.md): the conventional gradient echo
3. [](./03-epi.md): echo-planar imaging
4. [](./04-undersampling.md): k-space undersampling
5. [](./05-sense.md): parallel imaging with SENSE
6. [](./06-grappa.md): parallel imaging with GRAPPA
7. [](./08-epilogue.md): conclusion

:::{note}
Built with [MyST Markdown](https://mystmd.org): Markdown for the prose, Jupyter notebooks for the computation, one `myst.yml` for the configuration, and a GitHub Action that rebuilds and republishes on every push.
:::