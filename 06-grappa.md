---
title: GRAPPA - Parallel imaging in k-space
---

## Scientist E: a different way to use the team

:::{figure} images/comics/06-grappa.svg
:label: comicGrappa
:alt: Grappa asks the four painters to paint the middle of the canvas completely, then fills in every missing line by guessing from its neighbours.
:::

Scientist E likes the idea of having four painters work at the same time. But he does not like the SENSE method: it needs a separate reference scan to measure each coil’s sensitivity, and if the flower moves between the reference scan and the accelerated scan, the unfolding can become inaccurate.

So he proposes a different strategy: instead of unfolding the folded image, fill in the missing k-space lines before reconstructing the image.

His plan has two steps.

1. A common zone. The four painters still skip lines, except in the middle of the canvas, where they all paint a small band of lines completely.
2. Learn, then guess. From this fully sampled band, they learns a rule for predicting a missing line from nearby acquired lines on all four canvases. They then applies this rule to the rest of k-space.

The scanner therefore starts with four incomplete k-spaces, learns how the coils are related from the fully sampled band, and uses this information to synthesize the missing lines.

| In the comic | In the scanner |
|---|---|
| Four painters working at the same time | Several receive coils acquiring the signal simultaneously|
| The fully painted band in the middle | The auto-calibration signal (ACS) lines at the centre of k-space |
| Learning the rule from the common zone | Fitting the GRAPPA weights (the "kernel") by least squares |
| Guessing each missing line from its neighbours | Synthesising the missing k-space lines of each coil |
| Four complete canvases | Four complete k-spaces (one by coil), reconstructed by IFFT and then combined|


## How Grappa guesses a missing point

The signal measured by different coils is not independent: all coils observe the same object, but with different spatial sensitivities. This creates structured relationships between their k-space data. GRAPPA exploits these relationships locally {cite:p}`Griswold2002`. A missing k-space point in one coil can be predicted from nearby acquired points across all coils. The coefficients used to make this prediction are called the GRAPPA weights, or the kernel. Each coil has its own set of weights.

:::{important} The key idea is simple
Learn the prediction rule where all the data are known, then use that rule where data are missing.
:::

Move the slider to follow the process:

:::{figure} #figGrappaKernelbis
:label: grappaKernel
GRAPPA step by step ($R = 2$). Grey dots: acquired lines. Empty circles: skipped lines. Green dots, inside the dotted box: the common zone (ACS). Coloured rings: the points used, above and below, in each coil. Star: the point to find in coil 1. The equation above the figure is written in the colour of each coil. The numbers are made up to keep the example simple.
:::

Steps 1 and 2: learn. Inside the ACS region, every line is acquired, so both the target and all its neighbours are known. At one position of the kernel, the target gives one equation for the unknown weights. Sliding the kernel across the ACS region provides many more equations, all involving the same weights. The computer finds the weights that best fit all of these examples simultaneously.

Steps 3 and 4: apply. Outside the ACS region, the target may lie on a skipped line, so its value is unknown. However, the neighbouring acquired points are available. The computer multiplies them by the learned weights and adds the results to predict the missing target. This process is repeated for every missing point and every coil (each coil has its own weights).

## Learning the weights from the ACS lines

Suppose we have four coils and use a simple kernel containing the point immediately above and below the target. To reconstruct a point in coil 1, we therefore need eight weights: two neighbouring points from each of the four coils.

$$
\begin{aligned}
S_1(\text{target}) = \;
& w_1\,S_1(\text{above}) + w_2\,S_1(\text{below})
+ w_3\,S_2(\text{above}) + w_4\,S_2(\text{below}) \\
+ \;& w_5\,S_3(\text{above}) + w_6\,S_3(\text{below})
+ w_7\,S_4(\text{above}) + w_8\,S_4(\text{below})
\end{aligned}
$$ (eqGrappaSimple)

Where $S_c(\text{above})$ and $S_c(\text{below})$ are the acquired k-space values from coil $c$ immediately above and below the target.

Inside the ACS region, every line is acquired, so the target and all eight neighbours are known. At one kernel position (step 1 of the slider), for example, we might obtain:

$$ 1.08 = 1.2\,w_1 + 0.8\,w_2 + 0.5\,w_3 + 0.3\,w_4 + 0.7\,w_5 + 0.4\,w_6 + 0.2\,w_7 + 0.6\,w_8 $$ (eqGrappaLearn)

This time, the unknowns are not the image values. They are the GRAPPA weights.

One kernel position gives one equation. Moving the kernel to another position in the ACS region gives another equation involving the same eight weights (step 2 of the slider). A 24-line ACS region with 256 readout points therefore provides thousands of training examples for only eight unknown weights. Stacking all these equations gives:

Stacking all these equations gives:

$$
\underbrace{\mathbf{b}}_{\text{known targets}}
=
\underbrace{\mathbf{A}}_{\text{known neighbours}}\;
\underbrace{\mathbf{w}}_{\text{unknown weights}}
$$

and the least-squares solution is:

$$
\hat{\mathbf{w}}
=
\left(\mathbf{A}^H\mathbf{A}\right)^{-1}
\mathbf{A}^H\mathbf{b}
$$ (eqGrappaMatrix)

Each row of $\mathbf{A}$ contains the neighbouring acquired points from one kernel position, while the corresponding entry of $\mathbf{b}$ contains the
known target. Because there are many more training examples than weights, the computer chooses the weights that best fit all of them.


## Applying the rule

Suppose the ACS region has given us:

$$
w_1 = 0.5,\; w_2 = 0.3,\; w_3 = 0.2,\; w_4 = -0.1,\;
w_5 = 0.1,\; w_6 = 0.2,\; w_7 = -0.2,\; w_8 = 0.1
$$

Now move the kernel outside the ACS region onto a skipped line (step 3 and 4 of the slider). The target is missing, but the lines immediately above and below it were acquired:

| | Coil 1 | Coil 2 | Coil 3 | Coil 4 |
|---|---|---|---|---|
| above | 1.4 | 0.6 | 0.5 | 0.3 |
| below | 1.0 | 0.2 | 0.8 | 0.4 |

The missing point is then:

$$
\begin{aligned}
S_1(\text{target}) &= 0.5 \cdot 1.4 + 0.3 \cdot 1.0 + 0.2 \cdot 0.6 - 0.1 \cdot 0.2
+ 0.1 \cdot 0.5 + 0.2 \cdot 0.8 - 0.2 \cdot 0.3 + 0.1 \cdot 0.4 \\
&= 1.29 .
\end{aligned}
$$ (eqGrappaApply)

GRAPPA repeats this prediction for every missing point and every coil, using a set of weights trained for each coil. Once all missing k-space points have been filled, each coil has a complete k-space. The scanner can then reconstruct each coil image with an IFFT and combine the coil images, for example using root-sum-of-squares.

:::{important}
The numbers here are made up to keep the example simple. In a real reconstruction, the values and weights are complex numbers and the kernel is usually larger  but the principle remains the same:: use the fully sampled ACS data to learn a local linear prediction rule, then use that rule to fill the missing k-space data. With a kernel 3 points wide and 32 coils, each coil has $2 \times 3 \times 32 = 192$ weights when in our example they had only 8.
:::

## GRAPPA on the flower

In the simulation below, the kernel uses the acquired line above and below each missing line, three points wide, across the four coils, and they are 18 ACS lines.

:::{figure} #figGrappa
:label: grappa
GRAPPA with a 18 ACS lines. Without Grappa, the common zone alone already gives a blurry "ghost" of the flower mixed with the copies. After Grappa
fills the gaps, the copies disappear. As with SENSE, the image gets noisier as $R$ grows.
:::

## SENSE or GRAPPA?

| | SENSE | GRAPPA |
|---|---|---|
| Where it works | On the folded images (image domain) | On the k-space |
| What it needs | Sensitivity maps from a separate reference scan | A few fully sampled centre lines inside the scan |
| Strength | Mathematically optimal when the maps are accurate | Robust when the maps are hard to measure (motion, small FOV) |
| Weakness | Errors in the maps give residual folding | The ACS lines take extra time; kernel errors give residual artifacts |

Both methods pay the same price in noise, captured by the g-factor of Equation [](#eqGfactor).