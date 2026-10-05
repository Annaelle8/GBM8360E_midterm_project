---
title: Gradient echo (GRE) pulse sequence
---

## Scientist A idea

:::{figure} images/comics/01-gre.svg
:label: comicGre
:alt: Scientist A paints one line, then walks all the way back to the paint station.
:::

Scientist A method is careful. She dips her brush at the paint station, walks to the canvas, paints one line from left to right, then walks all the way back to the paint station but has to wait for the buckets to refill. She repeats this for every line of the canvas. It works perfectly, but most of her time is spent walking and waiting, not painting.

This is very similar to how a basic Cartesian GRE acquisition works: one line of k-space is acquired during each repetition of the sequence:

| In the comic | In the scanner |
|---|---|
| The buckets are filled with paint | Longitudinal magnetization $M_z$ align with the main magnetic field $B_0$ |
| Dipping the brush | RF exitation pulse tips the magnetization away from $B_0$ |
| Choosing which line to paint | Phase-encode gradient |
| The brush stroke from left to right | Readout gradient |
| Walking back and waiting for the bucket to refilled| Repetition time (TR) between successive RF pulse: the proton need time to realigne with $B_0$s |

## The sequence, one line at a time

A gradient-echo (GRE) sequence uses an RF excitation pulse followed by a series of magnetic-field gradients. The phase-encoding gradient selects the position of a k-space line, while the readout gradient generates the echo. Indeed, unlike a spin-echo sequence, a GRE does not use a 180° RF pulse to refocus the spins. Instead, the readout gradient is reversed to bring the spins back into phase and form the echo.

:::{figure} #figGreTiming
:label: greTiming
The GRE pulse sequence. Each repetition acquires one k-space line. The phase-encoding gradient changes from one repetition to the next, selecting a different $k_y$ position, while the readout gradient traverses the line and produces the echo.
:::

Each repetition therefore follows the same basic sequence:

1. Apply an RF excitation pulse.
2. Apply a phase-encoding gradient to select a k-space line.
3. Apply the readout gradient while recording the echo.
4. Wait until the next repetition.

:::{note}
Only the phase-encoding gradient changes from one repetition to the next, allowing the scanner to progressively fill k-space.
:::

## Watch the canvas fill up

The slider below shows Scientist A canvas after a given number of trips. On the left is her painting (the k-space), filled from top to bottom. On the right is what the Fourier transform machine would show if she stopped at that moment.

:::{figure} #figGreFill
:label: greFill
Scientist A's canvas trip after trip. Left: the k-space filled from the top. Right: what the Fourier transform machine would show if she stopped at that moment.
:::

:::{tip}
Try `n = 40` and `n = 56`. You'll see the flower appears when the middle row (`n = 48`) is crossed.
:::


## How long does it take?

We assume a GRE sequence with sequential cartesian acquisition where k-space is acquired line by line, with one line per TR from the top
of k-space to the bottom. The $n$-th $k_y$ line is acquired at [](#eqLineTime):

$$ t_n(k_y) = n \cdot TR + TE, \qquad n = 0, 1, \dots, N_{ky} - 1 $$ (eqLineTime)

So an image with $N_{ky}$ phase-encoding lines therefore takes about $N_{ky} \cdot TR$ seconds to acquire. This can lead to long scan times, particularly when a large number of phase-encoding lines is required. This motivates the development of accelerated acquisition techniques.
