---
title: Conclusion
---

## No free lunch

Every member of the crew made the painting faster, and every one of them paid for it with something. This is the most important message of the book: an MRI protocol is always a compromise between time, signal quality and artifacts.

| Scientist | Trick | What it gains | What it costs | Where you meet it |
|---|---|---|---|---|
| A | One line per TR | Clean, simple, strong signal per line | Very long scans | Rarely used alone today |
| B | All lines after one pulse (EPI) | Very fast | Blurring ($T_2^*$) and ghostings | Functional MRI, diffusion MRI |
| C | Skip lines by a factor $R$ | $R$ times faster | Aliasing | Never used alone|
| D | SENSE: coil sensitivities unfold the image | Removes the aliasing | Noise amplification, needs a reference scan | Almost every clinical exam |
| E | GRAPPA: learn to fill the k-space from the centre | Removes the aliasing, self-calibrated | Noise amplification, extra ACS lines | Almost every clinical exam |

:::{note}
Some of these methods can be combined to accelerate the acquisition time even more as GRAPPA and EPI.
:::

## Other existing technics

- Simultaneous Multi-Slice (SMS): excite several slices at the same time and separate them with the coils.
- Compressed Sensing: skips lines at random space instead of regularly, so the missing information looks like noise that can be removed.
- Deep-learning reconstruction: A neural network trained on thousands k-space to guess the missing lines.

## References

Some references used to build this book:

- Larson, Peder E. Z. (2026) Principles of MRI. Retrieved from https://larsonlab.github.io/MRI-education-resources. doi: 10.5281/zenodo.5547020: used to learn some MRI physics concepts
- Claude (Anthropic): used to generate the comics and to help build the flower simulations.