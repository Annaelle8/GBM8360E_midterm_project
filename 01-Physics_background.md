---
title: Physics background - K-space
---

## Kspace definition

MRI  does not acquire images directly. Instead, it acquires the data as samples in the frequency domain, known as k-space:

The relationship between the image-domain signal $I(x,y)$ and its k-space representation $K(k_x,k_y)$ is given by the Fourier transform [](eqKspace):

$$K = \mathcal{F}(I)$$ (eqKspace)

where $\mathcal{F}$ represents the Fourier transform.

::: {note} Complex data
K-space data are complex values. Each sample therefore contains both magnitude and phase information.
:::


## Mathematical formulation

The continuous 2D Fourier $\mathcal{F}$ transform allow to convert the image domain data $(x,y)$ to the frequency domain $(k_x,k_y)$ [](#eqFFT) :

$$ K(k_x,k_y) = \iint I(x,y) \,e^{-i2\pi(k_xx+k_yy)} \,dx\,dy $$ (eqFFT)

The corresponding inverse Fourier transform reconstructs the image from k-space [](#eqIFFT):

$$ I(x,y) = \iint K(k_x,k_y) \,e^{i2\pi(k_xx+k_yy)} \,dk_x\,dk_y $$ (eqIFFT)

These two domains contain the exact same information, there just represented in different ways [](#eqFourierlink):

```{math}
:label: eqFourierLink
:typst: I(x, y) quad stretch(arrow.l.r)^cal(F)_(cal(F)^(-1)) quad K(k_x, k_y)
\boxed{I(x, y) \;\xleftrightarrow[\mathcal{F}^{-1}]{\mathcal{F}}\; K(k_x, k_y)}
```

::: {note} Fast Fourier Transform
In practice, MRI acquires a finite set of discrete samples in k-space. Numerical reconstruction therefore uses the 2D Fast Fourier Transform (FFT) and its inverse (IFFT).
:::

## Python formulation

Using NumPy, a centered k-space representation can be computed with a 2D Fast Fourier Transform (FFT):

```{code-block} python
import numpy as np
K = np.fft.fftshift(np.fft.fft2(np.fft.ifftshift(I)))
```
::: {note} Convention
Here, `fftshift` moves the zero frequency to the center of the array, which is the conventional way of displaying k-space.
:::

Image reconstruction is performed using the inverse transform (IFFT):

```{code-block} python
I = np.fft.ifftshift(np.fft.ifft2(np.fft.fftshift(K)))
```

The reconstructed image is complex-valued. Its magnitude and phase can be obtained as:

```{code-block} python
magnitude = np.abs(I)
phase = np.angle(I)
```

The figure [](#kspace_image) below shows the k-space data acquired from a brain slice together with the corresponding magnitude and phase images.

:::{figure} #figkspace_image
:label: kspace_image
K-space and corresponding image-domain magnitude and phase.
:::

:::{note}
The k-space data and reconstructed image shown above will be used as the reference dataset for the rest of this book.
:::

## Kspace properties

Each point $(k_x, k_y)$ in k-space encodes a particular spatial frequency component of the image. 

:::{figure} #figWaves
:label: waves
Every point of k-space encode a specific spatial frequency.
:::

:::{tip}
Pick a point on the canvas with the slider and look at the stripes it adds to the picture
:::

As we move farther away from the center of k-space, more the stripes get thinner. This implies that frequency increases with the distance from the center of k-space. Consequently, the center and periphery of k-space contribute differently to the reconstructed image.


The **center** of k-space contains low frequencies information: overall signal intensity, contrast and global structure. Keeping only the central region of k-space therefore produces an image with the main anatomical structures preserved, but with reduced spatial detail [](#Keep_kspace_center).

:::{figure} #figKeep_kspace_center
:label: Keep_kspace_center
Reconstruction using only the central region of k-space.
:::

:::{note}
The magnitude image appears blurred compared with the reference image because the outside regions of k-space have been removed. This reduces k_max, which leads to a lower spatial resolution according to $\Delta x \approx 1/(2k_{\max})$. However, since the k-space sampling interval ${\Delta k}$ remains unchanged, the field of view remains approximately the same, since $FOV = \frac{1}{\Delta k}$.
:::

The **periphery** contains high frequencies information: edges, fine structures and sharp details. Removing the central region while retaining the peripheral data therefore has a very different effect on the reconstructed image, only the edge of the brain is visible [](#Mask_kspace_center).

:::{figure} #figMask_kspace_center
:label: Mask_kspace_center
Reconstruction after removing the central region of k-space.
:::

## Play with these properties

The previous examples showed what happens when we keep or remove specific regions of k-space. We can now explore how the contribution of different spatial frequencies affects the reconstructed image by progressively adding them to k-space.

:::{figure} #figCentreOut
:label: centreOut
Adding the ingredients from the centre outwards. Left: the part of k-space used. Right: the resulting picture.
:::

:::{tip}
The center of kspace contained overall shape and brightness of the flower while the outer ones add the sharp edges of the petals.
:::

We observe the same behavior as before: the center of k-space mainly contributes to the image’s overall contrast and structure, while the outer regions contribute fine details and sharp edges.

:::{figure} #figCentreEdges
:label: centreEdges
K-space properties: the centre of k-space carries the contrast, the edges carry the details.
:::


## A key consequence of Fourier encoding

Fourier encoding also explains why k-space artifacts do not necessarily remain localized in the reconstructed image. Indeed, a localized corruption in k-space affects a large region of the image after the IFFT. For example, corruption of a single k-space line can produce a structured artifact extending across the image, rather than a small localized defect [](#KspaceImpulse).

:::{figure} #figKspaceImpulse
:label: KspaceImpulse
Simulation of a single error in kspace
:::

:::{warning} A critical consequence
Because image reconstruction is a Fourier transform, a localized error in k-space can propagate throughout the reconstructed image and produce a global structured and spatially distributed artifact.
:::