"""Shared helpers for "The k-Space Painters".

Every chapter imports this module, so the flower, the coils and the plotting style
are identical across the whole book. Convention used everywhere:

    axis 0 (rows, vertical)    = phase-encode direction  -> the "lines" we paint
    axis 1 (columns, horizontal) = readout direction      -> painted in one stroke
"""
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots

N = 96  # matrix size: divisible by 2, 3 and 4 so every acceleration factor works


# --------------------------------------------------------------------------- setup
def setup_plotly():
    """Emit interactive + PNG (for the PDF) when possible, like the template does."""
    try:
        pio.to_image(go.Figure(), format="png")
        pio.renderers.default = "plotly_mimetype+png"
    except Exception:
        pio.renderers.default = "plotly_mimetype"


# ------------------------------------------------------------------------- object
def flower(n=N):
    """The object our scientists want to digitise: a flower with a stem and leaves.

    It is deliberately tall so that folding (aliasing) along the vertical axis
    makes the copies overlap in an obvious way.
    """
    y, x = np.mgrid[-1:1:1j * n, -1:1:1j * n]
    img = np.zeros((n, n))

    # petals (6 of them), centred in the upper half
    cy = -0.30
    r = np.hypot(x, y - cy)
    th = np.arctan2(y - cy, x)

    petal_edge = 0.20 + 0.28 * np.abs(np.cos(3 * th)) ** 0.7
    petal_mask = r < petal_edge

    # Identify the 6 petals from their angular position
    # Each petal is centred on one of the six maxima of |cos(3*theta)|.
    petal_angle = np.arctan2(np.sin(6 * th), np.cos(6 * th))
    petal_id = ((petal_angle + np.pi) / (2 * np.pi) * 6).astype(int) % 6

    petal_levels = [0.70, 0.71, 0.70, 0.71, 0.70, 0.71]

    for i, level in enumerate(petal_levels):
        img[petal_mask & (petal_id == i)] = level

    # heart
    img[r < 0.13] = 1.0

    # stem
    img[(np.abs(x + 0.02 * np.sin(6 * y)) < 0.035) & (y > cy + 0.15) & (y < 0.88)] = 0.45

    # two leaves
    for sx, ly in ((1, 0.45), (-1, 0.62)):
        u = (x - sx * 0.17) * np.cos(sx * 0.6) + (y - ly) * np.sin(sx * 0.6)
        v = -(x - sx * 0.17) * np.sin(sx * 0.6) + (y - ly) * np.cos(sx * 0.6)
        img[(u / 0.19) ** 2 + (v / 0.07) ** 2 < 1] = 0.5

    # a flower pot at the bottom
    img[(y > 0.80) & (y < 0.97) & (np.abs(x) < 0.22 - 0.1 * (0.97 - y))] = 0.3
    return img


# ------------------------------------------------------------------------ fourier
def fft2c(img):
    """Image -> k-space (centred)."""
    return np.fft.fftshift(np.fft.fft2(np.fft.ifftshift(img, axes=(-2, -1))), axes=(-2, -1))


def ifft2c(k):
    """k-space -> image (centred). This is 'the scanner' of the story."""
    return np.fft.fftshift(np.fft.ifft2(np.fft.ifftshift(k, axes=(-2, -1))), axes=(-2, -1))


def to_u8(a, vmax=None):
    """Magnitude, scaled to 0-255 integers: keeps the web pages light."""
    a = np.abs(a)
    vmax = a.max() if vmax is None else vmax
    return np.clip(255 * a / (vmax + 1e-12), 0, 255).astype(np.uint8)


def kspace_u8(k, floor=None):
    """Log-magnitude of k-space so the faint outer stripes stay visible."""
    m = np.log1p(np.abs(k))
    return to_u8(m, m.max() if floor is None else floor)


# -------------------------------------------------------------------------- coils
def coil_maps(n=N, ncoils=4):
    """Smooth sensitivity maps: each 'painter' sees one part of the canvas best."""
    y, x = np.mgrid[-1:1:1j * n, -1:1:1j * n]
    # Staggered along the vertical (phase-encode) axis, so that every coil folds
    # differently -- that difference is what SENSE and GRAPPA exploit.
    centres = [(-1.3, -1.1), (-0.45, 1.25), (0.45, -1.25), (1.3, 1.1)][:ncoils]
    maps = []
    for i, (cy, cx) in enumerate(centres):
        mag = np.exp(-((y - cy) ** 2 + (x - cx) ** 2) / 2.0)
        phase = np.exp(1j * 0.6 * (i + 1) * (x * np.cos(i) + y * np.sin(i)))
        maps.append(mag * phase)
    maps = np.array(maps)
    return maps / np.sqrt((np.abs(maps) ** 2).sum(0)).max()


def rss(coil_imgs):
    """Root-sum-of-squares combination of coil images."""
    return np.sqrt((np.abs(coil_imgs) ** 2).sum(0))


def undersample(k, R, acs=0):
    """Keep every R-th phase-encode line (+ optionally a fully sampled centre)."""
    n = k.shape[-2]
    mask = np.zeros(n, bool)
    mask[::R] = True
    if acs:
        c = n // 2
        mask[c - acs // 2:c + acs // 2] = True
    out = np.zeros_like(k)
    out[..., mask, :] = k[..., mask, :]
    return out, mask


def sense(aliased_coil_imgs, maps, R, lam=0.005):
    """SENSE unfolding. aliased_coil_imgs: (ncoils, n, n) from every-R-th-line data.

    lam is a small Tikhonov regularisation, as used on real scanners, which stops the
    noise from exploding where the coils look too much alike.
    """
    nc, n, _ = maps.shape
    step = n // R
    out = np.zeros((n, n), complex)
    for y in range(step):
        ys = [(y + m * step) % n for m in range(R)]
        # For each column: solve  a = S rho   (nc equations, R unknowns)
        a = R * aliased_coil_imgs[:, y, :]                 # (nc, n)
        S = maps[:, ys, :].transpose(2, 0, 1)               # (n, nc, R)
        Sh = S.conj().transpose(0, 2, 1)
        rho = np.linalg.solve(Sh @ S + lam * np.eye(R), (Sh @ a.T[..., None]))[..., 0]
        out[ys, :] = rho.T
    return out


def grappa(k_under, mask, acs_rows, R):
    """Minimal GRAPPA along the phase-encode axis.

    For every missing line we learn, from the fully sampled centre (ACS), how to
    predict it from the acquired line just above and just below, 3 readout points
    wide, across all coils.
    """
    nc, n, nx = k_under.shape
    k = k_under.copy()
    acs = k_under[:, acs_rows, :]                      # (nc, nacs, nx)
    kx = np.arange(1, nx - 1)

    for off in range(1, R):                            # position of the missing line
        # --- training: slide the kernel through the ACS block
        src, tgt = [], []
        for y in range(off, acs.shape[1] - (R - off)):
            below, above = acs[:, y - off, :], acs[:, y - off + R, :]
            s = np.concatenate([below[:, kx - 1], below[:, kx], below[:, kx + 1],
                                above[:, kx - 1], above[:, kx], above[:, kx + 1]], 0)
            src.append(s.T)
            tgt.append(acs[:, y, kx].T)
        src, tgt = np.concatenate(src), np.concatenate(tgt)
        lam = 1e-3 * np.linalg.norm(src) ** 2 / src.shape[1]
        W = np.linalg.solve(src.conj().T @ src + lam * np.eye(src.shape[1]), src.conj().T @ tgt)

        # --- application: fill every missing line at this offset
        for y in range(n):
            if mask[y] or y - off < 0 or y - off + R >= n:
                continue
            if not (mask[y - off] and mask[y - off + R]):
                continue
            below, above = k[:, y - off, :], k[:, y - off + R, :]
            s = np.concatenate([below[:, kx - 1], below[:, kx], below[:, kx + 1],
                                above[:, kx - 1], above[:, kx], above[:, kx + 1]], 0)
            k[:, y, kx] = (s.T @ W).T
    return k


# ----------------------------------------------------------------------- plotting
GRAY = [[0, "black"], [1, "white"]]


def _heat(z):
    return go.Heatmap(z=z, colorscale=GRAY, zmin=0, zmax=255, showscale=False,
                      hovertemplate="row %{y}, col %{x}<extra></extra>")


def slider_panels(frames, labels, titles, default=0, prefix="", height=420):
    """Side-by-side grayscale panels driven by one slider.

    frames: list (one per slider position) of lists (one per panel) of uint8 arrays.
    The slider does not compute: every frame is precomputed and it just chooses.
    """
    npan = len(titles)
    fig = make_subplots(rows=1, cols=npan, subplot_titles=titles,
                        horizontal_spacing=0.03)
    for f, panels in enumerate(frames):
        for p, z in enumerate(panels):
            tr = _heat(z)
            tr.visible = (f == default)
            fig.add_trace(tr, row=1, col=p + 1)

    steps = []
    for f, lab in enumerate(labels):
        vis = [False] * (len(frames) * npan)
        vis[f * npan:(f + 1) * npan] = [True] * npan
        steps.append(dict(method="update", args=[{"visible": vis}], label=str(lab)))

    fig.update_layout(
        sliders=[dict(active=default, steps=steps, pad={"t": 30},
                      currentvalue={"prefix": prefix})],
        height=height, margin=dict(l=10, r=10, t=40, b=10),
        template="plotly_white",
    )
    for p in range(npan):
        ax = "" if p == 0 else str(p + 1)
        fig.update_layout(**{
            f"xaxis{ax}": dict(visible=False, scaleanchor=f"y{ax}", constrain="domain"),
            f"yaxis{ax}": dict(visible=False, autorange="reversed", constrain="domain"),
        })
    return fig


def static_panels(panels, titles, height=300):
    """Same look as slider_panels, without a slider."""
    return slider_panels([panels], [""], titles, height=height).update_layout(sliders=[])
