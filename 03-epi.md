---
title: Echo-planar imaging (EPI)
---


## Scientist B idea

:::{figure} images/comics/03-epi.svg
:label: comicEpi
:alt: Scientist B carries all the paint buckets and paints the canvas in a zigzag, left then right.
:::

Scientist B takes all the paint with him in a single trip, paints the first line from left to right, steps down, paints the next line from right to left, and zigzags down the whole canvas without ever stopping.

| In the comic | In the scanner |
|---|---|
| Taking all the paint at once | One RF excitation for the whole image (single-shot EPI) |
| Painting left, then right, then left... | A readout gradient that alternates in sign |
| Stepping down one line | A short phase-encode blip between echoes |

## GRE versus EPI-GRE

This pulse sequences readout all k-space lines sequentially for faster imaging. It is commonly used for diffusion-weighted imaging and fMRI.

:::{figure} #figEpiTrajectory
:label: epiTrajectory
In a clasique GRE every line needs its own repetition. In EPI the path never stops.
:::

In this sequence only one single RF pulse is used and then every line of k-space is acquired from the signal it created. The readout gradient
flips back and forth (left, right, left, right) and a tiny "blip" of the phase-encode gradient between each stroke moves the brush one line down.

:::{figure} #figEpiTiming
:label: epiTiming
A single RF pulse is followed by the whole echo train. The readout gradient changes sign for every line (the zigzag), and a small phase-encode blip moves the brush one line down. ESP is the echo spacing, the time to paint one line. TE is measured to the echo of the central line, which sets the contrast.
:::

## The signal fades: $T_2^*$ blurring

The EPI weakness is time. The signal that comes from a single RF pulse fades with times. Because the scanner puts the middle of the echo in the center of the k-space, the fading mostly hits the outer lines, which carry the fine details. The result is a blurrier image, especially for tissues with a short $T_2^*$.

In this simulation each line takes 0.5 ms, so the whole canvas takes 48 ms.

:::{figure} #figEpiBlur
:label: epiBlur
$T_2^*$ blurring in EPI. Each line takes 0.5 ms, so the 96 lines take 48 ms. The shorter the $T_2^*$, the more the late lines fade and the blurrier the flower.
:::

## The pattern is not perfect: ghosts

Acquiring the k-space lines in two directions can create ghosting artifact when imperfections such as eddy currents can make these two trajectories slightly different, introducing a phase difference between alternating lines. When the image is reconstructed, this inconsistency produces faint shifted copies of the object, known as Nyquist ghosting.

:::{figure} #figEpiGhost
:label: epiGhost
EPI ghost: a phase mismatch between the left-to-right and right-to-left lines creates a faint copy shifted by half the field of view.
:::