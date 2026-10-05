---
title: SENSE - parallel imaging in the image domain
---

## Scientist D idea

:::{figure} images/comics/05-sense.svg
:label: comicSense
:alt: Four painters with differently coloured goggles; a computer turns a folded picture into a single flower.
:::

Scientist C showed that painting fewer lines is fast but leaves copies. Scientist D decide to work with three of his fellow scientist. Each one of them the has their own canvas and they all paint only one line out of two, the same lines, at the same moment. Each of their four paintings, put in the scanner, shows a pile of folded flowers the same way as scientist C experiment. But the four painters are not identical. Indeed, there were not seeing the flower from the exact same angle, and therefore see certain parts brighter and the opposites darker. Their four folded pictures are therefore folded differently and do not contained the exact same infomation.

| In the comic | In the scanner |
|---|---|
| Four painters working at the same time | Several receive coils acquiring the signal simultaneously |
| Each painter on their own canvas | Each coil records its own k-space |
| Coloured goggles: each sees one part best | Coil sensitivity maps: each coil is most sensitive to the tissue closest to it |
| Everyone skips the same lines | Undersampling by a factor $R$ shared by all coils |
| The computer unfolds the picture | SENSE reconstruction (image domain) |

## SENSE

SENSE needs a short, low-resolution reference scan to measure the sensitivity map of each coil before the real acquisition {cite:p}`Pruessmann1999`.

:::{figure} #figCoilMaps
:label: coilMaps
Sensitivity map of each of the four coils.
:::

If the k-space of each coil were fully sampled, we would get four perfect flowers but with a different intensity pattern accros the image because each coil has a different spatial sensitivity.

:::{figure} #figCoilImages
:label: coilImages
The same flower seen by each coil.
:::

:::{note}
The individual coil images can then be combined, for example using an RSS or SNR-weighted coil combination.
:::

Now consider accelerated imaging. Instead of acquiring all k-space lines, each coil acquires only a fraction of them. Here, with an acceleration factor of $R=2$, the missing lines cause the image to fold: two spatially separated copies of the flower overlap in the same reconstructed image. The copies overlap in the same way for every coil, but their brightness differs: this difference is the extra information SENSE uses to determine which signal belongs to which spatial location and so unfold the image.

:::{figure} #figCoilFolded
:label: coilFolded
The folded picture from each coil, with $R = 2$. The copies overlap in the same way for every coil, but their brightness differs: this difference is the extra information SENSE uses to unfold the image.
:::

## Unfolding, pixel by pixel

Let’s zoom in on a single pixel of a folded image acquired with $R=2$ using two coils.

With $R=2$, the image is folded so that two points from the original image are mapped onto the same pixel. In our example, point $A$ lies on a petal in the top half of the flower, while point $B$ lies on the pot in the bottom half. They are separated by exactly half the FOV, so they end up at the same pixel after folding. The problem is that we no longer see $A$ and $B$ separately. Each coil measures a weighted mixture of their true signals. The weights are given by the coil sensitivities: a coil that is close to a point sees it more strongly, while a coil that is farther away sees it more weakly.

:::{figure} #figSenseExample
:label: senseExample
The example on the flower. (1) Coil 1 is above the flower while coil 2 is below it. Point A on a petal and point B on the pot are exactly half the FOV apart. Coil 1 sees A well (0.9) and B poorly (0.2); coil 2 does the opposite (0.3 and 0.8). In each folded image, A and B land on the same pixel, so each coil only measures a mix of the two. SENSE uses these two measurements and the known coil sensitivities to recover the original values of $A$ and $B$. The numbers are those of the example; brightness is shown in arbitrary units.
:::

From the reference scan, we know the sensitivity of each coil at each location. For this example:

| | Sensitivity at $A$ | Sensitivity at $B$ | Measured folded signal |
|---|---|---|---|
| coil 1 | 0.9 | 0.2 | 10 |
| coil 2 | 0.3 | 0.8 | 7 |

These sensitivities tell us how strongly each coil responds to each point. Therefore, the signal measured by each coil is the sum of the two true signals, weighted by the corresponding sensitivities:

$$
\begin{aligned}
\text{Coil 1:}\quad  & 0.9\,A + 0.2\,B = 10 \\
\text{Coil 2:}\quad & 0.3\,A + 0.8\,B = 7
\end{aligned}
$$ (eqSenseExample)

This gives us a system of two equations that we can solve, we have two measurements for the same two unknowns, $A$ and $B$. Because the two coils have different sensitivity patterns, the two measurements contain different information about the two points.

We found:

$$
\begin{aligned}
A &= 10 \\
B &= 5
\end{aligned}
$$
The folded pixel is now unfolded: the petal point has a brightness of 10 and the pot point a brightness of 5. The computer performs this same calculation for every folded pixel, recovering the two original locations and intensity and thereby unfolding the entire image.

### The general recipe

Our previous example can be written in a more compact way :

$$
\underbrace{\begin{bmatrix} 10 \\ 7 \end{bmatrix}}_{\text{measured}}
=
\underbrace{\begin{bmatrix} 0.9 & 0.2 \\ 0.3 & 0.8 \end{bmatrix}}_{\text{known from the reference scan}}
\underbrace{\begin{bmatrix} A \\ B \end{bmatrix}}_{\text{unknown}}
$$ (eqSenseExampleMatrix)

This representation gives back exactly the two equations of [](#eqSenseExample): first row $0.9\,A + 0.2\,B = 10$, second row
$0.3\,A + 0.8\,B = 7$.

In a real scanner there are $N_c$ coils, and with an acceleration factor $R$, each folded pixel is a mix of $R$ points of the real image, spaced by $\text{FOV}/R$. Call their positions $y_1, y_2, \dots, y_R$. For coil $c$, the folded pixel is:

$$ a_c = S_c(y_1)\,\rho(y_1) + S_c(y_2)\,\rho(y_2) + \dots + S_c(y_R)\,\rho(y_R), $$ (eqSenseOne)

and writing this equation for all the coils at once gives :

$$
\boxed{\;\mathbf{a} = \mathbf{S}\,\boldsymbol{\rho}\;}
\qquad\text{with}\qquad
\underbrace{\begin{bmatrix} a_1 \\ a_2 \\ \vdots \\ a_{N_c} \end{bmatrix}}_{\mathbf{a}\;(N_c \times 1)}
=
\underbrace{\begin{bmatrix}
S_1(y_1) & S_1(y_2) & \cdots & S_1(y_R) \\
S_2(y_1) & S_2(y_2) & \cdots & S_2(y_R) \\
\vdots & \vdots & \ddots & \vdots \\
S_{N_c}(y_1) & S_{N_c}(y_2) & \cdots & S_{N_c}(y_R)
\end{bmatrix}}_{\mathbf{S}\;(N_c \times R)}
\underbrace{\begin{bmatrix} \rho(y_1) \\ \rho(y_2) \\ \vdots \\ \rho(y_R) \end{bmatrix}}_{\boldsymbol{\rho}\;(R \times 1)}
$$ (eqSenseMatrix)

Where:

| Symbol | Size | What it is | In our example | Where it comes from |
|---|---|---|---|---|
| $\mathbf{a}$ | $N_c$ values | The value of the same pixel in the folded image of each coil | $(10,\ 7)$ | Measured in the fast, undersampled scan |
| $\mathbf{S}$ | $N_c$ rows × $R$ columns | The sensitivities: row $c$** says how well coil $c$ sees each of the $R$ points; column $r$ says how point $y_r$ is seen by all the coils | $\begin{bmatrix} 0.9 & 0.2 \\ 0.3 & 0.8 \end{bmatrix}$ | Known from the sensitivity maps of the reference scan |
| $\boldsymbol{\rho}$ | $R$ values | The true brightness of the $R$ points that fell on top of each other | $(A,\ B)$ | Unknown: this is what we want |
| $N_c$ | | Number of coils  | 2 | The coil array |
| $R$ | | Acceleration factor: number of unknowns per pixel | 2 | Chosen by the operator |


SENSE solves this system. If there are exactly as many coils as copies ($N_c = R$), $\mathbf{S}$ is square, so we have $\hat{\boldsymbol{\rho}} = \mathbf{S}^{-1}\mathbf{a}$ and we solve the system exactly as we did by hand. With more coils than copies ($N_c > R$), there are more equations than unknowns. Because of noise, they never agree perfectly, so SENSE takes the values that fit all of them best, in the least-squares sense:

$$ \boxed{\;\hat{\boldsymbol{\rho}} = \left(\mathbf{S}^H \mathbf{S}\right)^{-1} \mathbf{S}^H \mathbf{a}\;} $$ (eqSense)

How to read it, from right to left:

- $\mathbf{S}^H$ is the conjugate transpose of $\mathbf{S}$: rows and columns are swapped (and, since real sensitivities are complex numbers with a phase, the phase is reversed). $\mathbf{S}^H \mathbf{a}$ combines the measurements of all the coils, giving more weight to the coils that see each point well.
- $\mathbf{S}^H \mathbf{S}$ is a small $R \times R$ matrix that describes how much the points are mixed up together.
- Its inverse, $\left(\mathbf{S}^H \mathbf{S}\right)^{-1}$, undoes that mixing.
- $\hat{\boldsymbol{\rho}}$ is the "best estimate" of the true $\boldsymbol{\rho}$.

Two conditions must hold:

1. At least as many coils as the undersampling factor: $N_c \geq R$. Otherwise there are fewer equations than unknowns, and the problem has no single answer.
2. The coils must see differently: if two columns of $\mathbf{S}$ are almost equal, the coils cannot tell the corresponding points apart, and the noise is strongly amplified. This is the g-factor of the next section.

Move the slider to see the folded pictures and the unfolded result. A little noise has been added to the data, as in a real scanner.

:::{figure} #figSense
:label: sense
SENSE with four coils and a little noise. Left: one coil's folded image. Middle: the four coils simply combined, still folded. Right: the SENSE result.
:::

## The price: noise amplification

At $R = 2$ the result is almost perfect, and at $R = 3$ it is only a little noisier. At $R = 4$, the quartet reaches its limit: four coils for $R=4$ means the equations can barely be told apart, and the result is noisy with some leftover folding. Two effects add up:
- First, fewer lines means less signal.
- Second, where the coils see the same thing, the equations are hard to tell apart and solving them amplifies the noise. This second effect is measured by the g-factor:

$$ \text{SNR}_R = \frac{\text{SNR}_\text{full}}{g\,\sqrt{R}}, \qquad g \geq 1. $$ (eqGfactor)

Modern head coils have 32 or 64 small coils, which keeps $g$ close to 1 for accelerations of 2 to 4.
