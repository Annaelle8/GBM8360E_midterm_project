---
title: Flash teleports
subtitle: Short TR, small flip angles and spoiling (FLASH)
---

:::{figure} images/comics/02-flash.svg
:label: comicFlash
:alt: Flash teleports back to the paint station, then wipes his brush and takes only a drop of paint.
:::

## Flash's two ideas

Flash watched Greta walk back and forth and had a simple thought: *why walk?* He
teleports back to the paint station, so each trip takes almost no time. In the scanner,
teleporting means using a **very short TR**, a few milliseconds instead of hundreds.

But teleporting creates two new problems, and Flash has an answer for each.

**Problem 1: the buckets don't have time to refill.** If Flash scoops a big brushful at
every trip, the buckets are empty after a few lines and the rest of the canvas is
painted with almost nothing. His answer: *take only a drop of paint each time.* A drop
is enough to paint a visible line, and the buckets can keep up.

**Problem 2: the brush is still wet.** Arriving so fast, some paint from the previous
line is still on the brush and would smear into the next line. His answer: *wipe the
brush before each new line.* This is what MRI physicists call **spoiling**.

| In the comic | In the scanner |
|---|---|
| Teleporting back | A short TR (typically 2 to 20 ms) |
| Taking only a drop of paint | A small flip angle $\alpha$ (for example 5° to 20°) instead of 90° |
| Buckets refilling during the trip | $M_z$ recovering with time constant $T_1$ |
| Leftover wet paint on the brush | Transverse magnetization still present from the previous repetition |
| Wiping the brush with a rag | Spoiling: a strong gradient at the end of each TR and/or a changing RF phase that scrambles the leftover signal |

## How big should the drop be?

With a short TR, the magnetization settles into a *steady state*: every repetition
starts with the same amount of paint in the buckets. For a spoiled GRE, the signal of
that steady state is

$$
S(\alpha) = M_0 \, \sin\alpha \, \frac{1 - E_1}{1 - E_1 \cos\alpha},
\qquad E_1 = e^{-\text{TR}/T_1}
$$ (eqSpgr)

Too big a drop empties the buckets; too small a drop paints a faint line. The best
choice, called the **Ernst angle**, is

$$
\cos\alpha_E = e^{-\text{TR}/T_1}.
$$ (eqErnst)

Move the slider: the shorter the TR (the faster Flash teleports), the smaller the ideal
drop.

:::{figure} #figErnst
:label: ernst
**Steady-state signal of a spoiled GRE.** Each curve is for one TR, with
$T_1 = 1000$ ms. With TR = 10 ms the best flip angle is only about 8°, and the signal
is small but perfectly usable, while each line takes fifty times less time than
Greta's.
:::

````{admonition} Reproduce this figure yourself
:class: tip, dropdown

The helpers come from `notebooks/painters.py`; copy it next to your notebook. The full code of the interactive figure, with its slider, is in `notebooks/figures.ipynb`.

Equations [](#eqSpgr) and [](#eqErnst) in a few lines of numpy.

```python
import numpy as np
import matplotlib.pyplot as plt

T1 = 1000.0                                      # ms
alpha = np.deg2rad(np.linspace(0.5, 90, 300))
for TR in (5, 10, 50, 500):                      # ms
    E1 = np.exp(-TR / T1)
    S = np.sin(alpha) * (1 - E1) / (1 - E1 * np.cos(alpha))
    plt.plot(np.rad2deg(alpha), S, label=f"TR = {TR} ms "
             f"(Ernst angle {np.rad2deg(np.arccos(E1)):.0f}°)")
plt.xlabel("flip angle (degrees)"); plt.ylabel("signal / M0"); plt.legend()
plt.show()
```
````

## Why wipe the brush?

When TR is shorter than the tissue's $T_2$, the sideways magnetization from the previous
line has not faded yet. Without spoiling it adds to the next echo, and the image gets a
mixed, hard-to-predict contrast and sometimes stripes. The "rag" is a strong gradient
pulse that twists this leftover magnetization into a random mess that averages to zero,
often combined with a phase of the RF pulse that changes from one line to the next.
After wiping, every line starts clean, and the contrast depends simply on $T_1$
through Equation [](#eqSpgr).

:::{note} The other option: keep the paint
Some sequences deliberately *keep* the leftover paint and reuse it, which gives more
signal (balanced SSFP, often called TrueFISP or FIESTA). That is a different story, with
different artifacts, and Flash leaves it to another crew.
:::

:::{admonition} Scan-time counter
:class: tip
256 lines × TR of 10 ms = **2.6 s per slice**, about fifty times faster than Greta.
The price is a smaller signal per line.
:::

:::{seealso} Who really had this idea?
The FLASH sequence (fast low-angle shot) was introduced by Axel Haase, Jens Frahm and
colleagues in Göttingen {cite:p}`Haase1986`, and it made fast 3D and dynamic MRI
practical. The optimal angle is named after Richard Ernst {cite:p}`Ernst1966`.
:::
