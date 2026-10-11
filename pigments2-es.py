import numpy as np
from pigment_molecules import add_molecule
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.colors import LinearSegmentedColormap
from matplotlib import font_manager
from matplotlib.offsetbox import AnnotationBbox, DrawingArea
from matplotlib.patches import Ellipse, Polygon, PathPatch
from matplotlib.path import Path

# Easy-to-tweak presentation settings.
FILL_PALETTE = "wavelength"  # "wavelength" or "turbo"
DARKEN_BY_REFLECTANCE = False
MARK_NEAR_INFRARED = False  # Approximate boundary; visibility fades gradually.
FONT_CHOICES = ["Comic Neue", "Comic Sans MS", "Chalkboard", "DejaVu Sans"]
available_fonts = {font.name for font in font_manager.fontManager.ttflist}
COMIC_FONT = next(name for name in FONT_CHOICES if name in available_fonts)


# ============================================================
# GLOBAL STYLE
# ============================================================

plt.rcParams.update({
    "font.family": COMIC_FONT,
    "pdf.fonttype": 42,
    "font.size": 13,
    "axes.linewidth": 2.5,
    "xtick.major.width": 2,
    "xtick.major.size": 6,
})

# Bright illustrative colors, without dimming at the limits of vision.
# Anchors keep green near 550 nm and red near 650 nm. Beyond ~700 nm
# red is symbolic: this portion of the plot extends into near infrared.
# NASA overview: https://science.nasa.gov/ems/09_visiblelight/
RAINBOW = LinearSegmentedColormap.from_list(
    "outreach_spectrum",
    [(0.0, "#8b38f5"), (0.125, "#2856ff"), (0.225, "#00cfff"),
     (0.325, "#20d85a"), (0.425, "#a6e52d"), (0.475, "#ffe331"),
     (0.55, "#ff922e"), (0.625, "#ff363b"), (1.0, "#ff363b")],
    N=1024,
)


def wavelength_to_rgb(wavelength):
    """Bright illustrative rainbow; use FILL_PALETTE to try turbo."""
    t = np.clip((wavelength - 400) / 400, 0, 1)
    if FILL_PALETTE == "turbo":
        # Trim turbo's dark ends. This is a decorative, not physical scale.
        return np.asarray(plt.get_cmap("turbo")(0.10 + 0.78 * t)[:3])
    return np.asarray(RAINBOW(t)[:3])


# ============================================================
# BASIC FUNCTIONS FOR BUILDING SPECTRA
# ============================================================

def gaussian(x, center, width):
    return np.exp(-0.5 * ((x - center) / width)**2)


def sigmoid(x, center, width):
    return 1.0 / (1.0 + np.exp(-(x - center) / width))


# Wavelength range
wl = np.linspace(400, 700, 700)


# ============================================================
# APPROXIMATE REFLECTANCE SPECTRA
# ============================================================
#
# These are intentionally simplified.
# They reproduce the qualitative color-producing behavior,
# not laboratory spectra of a particular sample.
# ============================================================


# These are illustrative OBJECT reflectances, not measured pure-pigment
# spectra or 1 - absorbance. Tissue scattering, concentration and other
# pigments also affect the observed curves. Xanthophyll is a pigment family;
# lutein represents the yellow xanthophylls here.
# Qualitative absorption references (not fits to these data):
# Betanin / beetroot measurements:
# https://pmc.ncbi.nlm.nih.gov/articles/PMC11360503/
# Beta-carotene absorption:
# https://www.omlc.org/spectra/PhotochemCAD/html/041.html
# Xanthophyll spectroscopy (including lutein):
# https://doi.org/10.1021/jacs.0c04619

# 1. BETANIN / RED BEET
# Strong green absorption around 535 nm; red reflection dominates, with
# a small blue-violet shoulder giving the beet its red-purple appearance.
betanin = np.clip(
    0.025
    + 0.105 * gaussian(wl, 425, 28)
    + 0.62 * sigmoid(wl, 603, 17),
    0, 1,
)

# 2. XANTHOPHYLL / YELLOW AUTUMN LEAF (LUTEIN-LIKE)
# Blue absorption; both green and red are reflected, producing yellow.
# This represents a yellow leaf with little remaining chlorophyll.
xanthophyll = np.clip(
    0.045
    + 0.69 * sigmoid(wl, 510, 16)
    + 0.035 * sigmoid(wl, 590, 35),
    0, 1,
)

# 3. BETA-CAROTENE / CARROT
# Strong absorption of blue / blue-green light; reflectance rises through
# green toward yellow, orange and red. A broader, later rise than the
# yellow-leaf example represents an orange carrot's tissue and pigments.
beta_carotene = np.clip(
    0.04
    + 0.72 * sigmoid(wl, 552, 22),
    0, 1,
)

# 4. CHLOROPHYLL / GREEN LEAF
# Blue and red absorption, green reflection maximum, and the beginning
# of the leaf's near-infrared red edge at the right-hand plot boundary.
chlorophyll = np.clip(
    0.055
    + 0.38 * gaussian(wl, 550, 32)
    + 0.72 * sigmoid(wl, 705, 10),
    0, 1,
)


# ============================================================
# RAINBOW FILL
# ============================================================

def rainbow_fill(ax, x, y, brightness=False):
    """
    Fill the region under a spectrum with wavelength-dependent
    colors.

    If brightness=True, low-reflectance parts are darker.
    """

    polygons = []
    colors = []

    for i in range(len(x) - 1):

        polygons.append([
            (x[i],     0),
            (x[i],     y[i]),
            (x[i + 1], y[i + 1]),
            (x[i + 1], 0)
        ])

        wavelength = 0.5 * (x[i] + x[i + 1])

        rgb = wavelength_to_rgb(wavelength)

        if brightness:
            # Don't make low-reflectance regions completely black.
            # This keeps the rainbow wavelength scale visible.
            strength = 0.40 + 0.60 * (
                0.5 * (y[i] + y[i + 1])
            )

            rgb = rgb * strength

        colors.append(rgb)

    collection = PolyCollection(
        polygons,
        facecolors=colors,
        edgecolors="face",
        linewidths=0.25,
        antialiaseds=False
    )

    ax.add_collection(collection)


def draw_object_icon(ax, kind, color):
    """Font-independent vector cartoons, editable entirely in Python."""
    box = DrawingArea(52, 52, 0, 0)
    ink = "#202020"

    def add(patch):
        box.add_artist(patch)

    def line(points, color=ink, width=2):
        xs, ys = zip(*points)
        box.add_artist(plt.Line2D(xs, ys, color=color, linewidth=width,
                                 solid_capstyle="round"))

    if kind == "beet":
        # Red-purple root, tapering tip, and leafy crown.
        for x, y, angle in [(15, 43, 35), (27, 46, 0), (38, 43, -35)]:
            line([(26, 32), (x, y)], "#9c2750", 2.5)
            add(Ellipse((x, y), 10, 17, angle=angle,
                        facecolor="#58b747", edgecolor=ink, linewidth=1.5))
        vertices = [(26, 35), (3, 40), (4, 17), (18, 11),
                    (22, 8), (24, 5), (25, 2),
                    (31, 10), (48, 16), (45, 29),
                    (42, 36), (33, 38), (26, 35), (26, 35)]
        add(PathPatch(Path(vertices, [Path.MOVETO] + [Path.CURVE4]*12
                           + [Path.CLOSEPOLY]), facecolor=color,
                      edgecolor=ink, linewidth=2))
        add(Ellipse((16, 27), 5, 10, angle=-25, facecolor="#ef8ca9"))
        line([(31, 15), (36, 18)], "#8c2047", 1.3)
    elif kind in ("leaf", "yellow_leaf"):
        vein = "#946620" if kind == "yellow_leaf" else "#205e32"
        if kind == "yellow_leaf":
            # Pointed autumn leaf, distinct from the green leaf's oval.
            add(Polygon([(12, 10), (8, 24), (13, 23), (10, 36),
                         (20, 33), (22, 49), (30, 39), (40, 47),
                         (40, 33), (48, 32), (38, 23), (43, 19),
                         (27, 12)], closed=True, facecolor=color,
                        edgecolor=ink, linewidth=2))
        else:
            add(Ellipse((27, 28), 26, 43, angle=-35, facecolor=color,
                        edgecolor=ink, linewidth=2))
        line([(10, 4), (38, 44)], vein)
        for x, y in [(20, 18), (26, 27), (32, 36)]:
            line([(x-8, y+2), (x, y), (x+3, y-8)], vein, 1.4)
    elif kind == "carrot":
        # Tapered orange root with three green fronds.
        for x, y in [(21, 49), (34, 51), (46, 44)]:
            line([(30, 37), (x, y)], "#287d36", 4)
        vertices = [(20, 37), (22, 43), (37, 43), (41, 35),
                    (38, 25), (19, 5), (10, 2),
                    (11, 14), (15, 30), (20, 37), (20, 37)]
        add(PathPatch(Path(vertices, [Path.MOVETO] + [Path.CURVE4]*9
                           + [Path.CLOSEPOLY]), facecolor=color,
                      edgecolor=ink, linewidth=2))
        line([(20, 31), (26, 28)], "#b95019", 1.5)
        line([(29, 23), (33, 25)], "#b95019", 1.5)
        line([(16, 17), (20, 15)], "#b95019", 1.5)
        line([(22, 35), (25, 37)], "#ffd075", 2)
    artist = AnnotationBbox(box, (0.0, 1.13), xycoords=ax.transAxes,
                            box_alignment=(0, 0.5), frameon=False,
                            annotation_clip=False)
    ax.add_artist(artist)


# ============================================================
# PANEL DRAWING FUNCTION
# ============================================================

def draw_panel(ax, spectrum, title, subtitle, object_color, icon):

    draw_object_icon(ax, icon, object_color)
    add_molecule(ax, icon, language="es")

    # Rainbow
    rainbow_fill(
        ax,
        wl,
        spectrum,
        brightness=DARKEN_BY_REFLECTANCE
    )

    # Thick dark outline
    ax.plot(
        wl,
        spectrum,
        color="#202020",
        linewidth=4,
        solid_capstyle="round",
        zorder=10
    )

    # --------------------------------------------------------
    # Axes
    # --------------------------------------------------------

    ax.set_xlim(400, 700)
    ax.set_ylim(0, 1.0)

    if MARK_NEAR_INFRARED:
        ax.axvline(700, color="#777777", linewidth=1.2,
                   linestyle=(0, (3, 4)), zorder=11)
        ax.text(750, 0.96, "Infrarrojo cercano", ha="center", va="top",
                fontsize=11, color="#555555")

    ax.set_xticks([400, 500, 600, 700])

    # Outreach figure: quantitative Y values aren't important
    ax.set_yticks([])

    ax.set_xlabel(
        "Longitud de onda (nm)",
        fontsize=15,
        fontweight="bold"
    )

    ax.set_ylabel(
        "Intensidad",
        fontsize=15,
        fontweight="bold",
        labelpad=14
    )

    # Only left/bottom spines
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.spines["left"].set_linewidth(2.5)
    ax.spines["bottom"].set_linewidth(2.5)

    # --------------------------------------------------------
    # LOW / HIGH
    # --------------------------------------------------------

    ax.text(
        -0.015, 0.02,
        "BAJA",
        transform=ax.transAxes,
        rotation=90,
        ha="right",
        va="bottom",
        fontsize=10,
        fontweight="bold"
    )

    ax.text(
        -0.015, 0.98,
        "ALTA",
        transform=ax.transAxes,
        rotation=90,
        ha="right",
        va="top",
        fontsize=10,
        fontweight="bold"
    )

    # --------------------------------------------------------
    # Title
    # --------------------------------------------------------

    ax.text(
        0.16, 1.13,
        title,
        transform=ax.transAxes,
        fontsize=18,
        fontweight="bold",
        va="center"
    )

    ax.text(
        0.16, 1.045,
        subtitle,
        transform=ax.transAxes,
        fontsize=12,
        va="center",
        color="#444444"
    )

# ============================================================
# CREATE FIGURE
# ============================================================

fig, axes = plt.subplots(
    2, 2,
    figsize=(15, 10),
    sharex=False,
    sharey=True
)

fig.patch.set_facecolor("#f7f7f4")


# Slightly warm background in panels
for ax in axes.flat:
    ax.set_facecolor("#f7f7f4")


# ------------------------------------------------------------
# Draw panels
# ------------------------------------------------------------

draw_panel(
    axes[0, 0],
    betanin,
    "BETANINA",
    "Betabel",
    "#bb2856",
    "beet"
)

draw_panel(
    axes[0, 1],
    xanthophyll,
    "XANTOFILA",
    "Hojas amarillas de otoño",
    "#f5ce32",
    "yellow_leaf"
)

draw_panel(
    axes[1, 1],
    beta_carotene,
    "BETACAROTENO",
    "Zanahorias",
    "#ff8a25",
    "carrot"
)

draw_panel(
    axes[1, 0],
    chlorophyll,
    "CLOROFILA",
    "Hojas verdes",
    "#54bb44",
    "leaf"
)


# ============================================================
# MAIN TITLE
# ============================================================

# fig.suptitle(
#     "¿POR QUÉ LOS OBJETOS TIENEN COLOR?",
#     fontsize=30,
#     fontweight="bold",
#     y=0.99
# )

# fig.text(
#     0.5,
#     0.945,
#     "Las longitudes de onda que refleja un objeto determinan el color que vemos",
#     ha="center",
#     fontsize=17
# )


# ============================================================
# SPACING
# ============================================================

plt.subplots_adjust(
    left=0.08,
    right=0.97,
    bottom=0.08,
    top=0.84,
    wspace=0.20,
    hspace=0.52
)


# ============================================================
# EXPORT
# ============================================================

plt.savefig(
    "pigments2-es.pdf",
    bbox_inches="tight"
)

plt.savefig(
    "pigments2-es.png",
    dpi=300,
    bbox_inches="tight"
)

# Colors above ~700 nm are illustrative, not visible red light.
# Spectra describe simplified objects, not isolated pigment measurements.
# plt.show()