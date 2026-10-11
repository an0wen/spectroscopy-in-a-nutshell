import numpy as np
from pigment_molecules import add_molecule
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.colors import LinearSegmentedColormap
from matplotlib import font_manager
from matplotlib.offsetbox import AnnotationBbox, DrawingArea
from matplotlib.patches import Circle, Ellipse, Polygon, PathPatch
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


# ------------------------------------------------------------
# 1. ANTHOCYANIN-RICH RED APPLE
#
# Anthocyanins absorb strongly in the green.
# Reflectance therefore rises dramatically toward red.
# ------------------------------------------------------------

anthocyanin = (
    0.06
    + 0.68 * sigmoid(wl, 600, 14)
    - 0.035 * gaussian(wl, 525, 45)
)

anthocyanin = np.clip(anthocyanin, 0, 1)


# ------------------------------------------------------------
# 2. CHLOROPHYLL / GREEN LEAF
#
# Blue absorption
# Green reflectance maximum
# Red absorption around ~660 nm
# Red edge near ~700 nm
# ------------------------------------------------------------

chlorophyll = (
    0.055
    + 0.38 * gaussian(wl, 550, 32)
    + 0.72 * sigmoid(wl, 705, 10)
)

chlorophyll = np.clip(chlorophyll, 0, 1)


# ------------------------------------------------------------
# 3. INDIGO-DYED JEANS
#
# Broad blue reflection, much less reflection at longer
# wavelengths.
# ------------------------------------------------------------

indigo = (
    0.045
    + 0.58 * gaussian(wl, 455, 45)
    + 0.025 * gaussian(wl, 650, 100)
)

indigo = np.clip(indigo, 0, 1)


# ------------------------------------------------------------
# 4. MELANIN
#
# Broad absorption throughout the visible.
# Reflectance gradually increases toward longer wavelengths.
# ------------------------------------------------------------

melanin = (
    0.045
    + 0.20 * ((wl - 400) / 400)
    + 0.10 * sigmoid(wl, 520, 50)
)

melanin = np.clip(melanin*1.5, 0, 1)


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

    if kind == "apple":
        vertices = [(26, 37), (3, 49), (4, 8), (20, 5),
                    (26, 3), (29, 5), (32, 5), (48, 8),
                    (49, 49), (26, 37), (26, 37)]
        add(PathPatch(Path(vertices, [Path.MOVETO] + [Path.CURVE4]*9
                           + [Path.CLOSEPOLY]), facecolor=color,
                      edgecolor=ink, linewidth=2))
        line([(26, 37), (29, 48)], "#795133", 3)
        add(Ellipse((36, 44), 16, 8, angle=25, facecolor="#62bf47",
                    edgecolor=ink, linewidth=1.5))
        add(Ellipse((15, 29), 5, 10, angle=-20, facecolor="#ffaca0"))
    elif kind == "leaf":
        add(Ellipse((27, 28), 26, 43, angle=-35, facecolor=color,
                    edgecolor=ink, linewidth=2))
        line([(10, 4), (38, 44)])
        for x, y in [(20, 18), (26, 27), (32, 36)]:
            line([(x-8, y+2), (x, y), (x+3, y-8)], "#205e32", 1.4)
    elif kind == "jeans":
        add(Polygon([(10, 48), (42, 48), (46, 5), (30, 5),
                     (26, 28), (22, 5), (6, 5)], closed=True,
                    facecolor=color, edgecolor=ink, linewidth=2))
        line([(11, 41), (41, 41)], "#ffc96a", 1.5)
        line([(26, 41), (26, 30)], "#ffc96a", 1.5)
        line([(12, 39), (18, 34), (21, 40)], "#a7d4ff", 1.4)
        line([(31, 40), (34, 34), (40, 39)], "#a7d4ff", 1.4)
    elif kind == "eye":
        # Brown iris: one example of melanin's contribution to color.
        add(Ellipse((26, 26), 48, 29, facecolor="white",
                    edgecolor=ink, linewidth=2))
        add(Circle((26, 26), 13, facecolor=color, edgecolor=ink, linewidth=1.5))
        add(Circle((26, 26), 6, facecolor=ink))
        add(Circle((22, 31), 3, facecolor="white"))
    artist = AnnotationBbox(box, (0.0, 1.13), xycoords=ax.transAxes,
                            box_alignment=(0, 0.5), frameon=False,
                            annotation_clip=False)
    ax.add_artist(artist)


# ============================================================
# PANEL DRAWING FUNCTION
# ============================================================

def draw_panel(ax, spectrum, title, subtitle, object_color, icon):

    draw_object_icon(ax, icon, object_color)
    add_molecule(ax, icon, language="en")

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
        ax.text(750, 0.96, "Near infrared", ha="center", va="top",
                fontsize=11, color="#555555")

    ax.set_xticks([400, 500, 600, 700])

    # Outreach figure: quantitative Y values aren't important
    ax.set_yticks([])

    ax.set_xlabel(
        "Wavelength (nm)",
        fontsize=15,
        fontweight="bold"
    )

    ax.set_ylabel(
        "Intensity",
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
        "LOW",
        transform=ax.transAxes,
        rotation=90,
        ha="right",
        va="bottom",
        fontsize=10,
        fontweight="bold"
    )

    ax.text(
        -0.015, 0.98,
        "HIGH",
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
    anthocyanin,
    "ANTHOCYANIN",
    "Red apple",
    "#ef3b43",
    "apple"
)

draw_panel(
    axes[0, 1],
    indigo,
    "INDIGO DYE",
    "Blue jeans",
    "#326bca",
    "jeans"
)

draw_panel(
    axes[1, 0],
    chlorophyll,
    "CHLOROPHYLL",
    "Plants",
    "#54bb44",
    "leaf"
)

draw_panel(
    axes[1, 1],
    melanin,
    "MELANIN",
    "Skin, hair, eyes",
    "#925831",
    "eye"
)


# ============================================================
# OPTIONAL ANNOTATIONS
# ============================================================

# # Green reflection from plants
# axes[1, 0].annotate(
#     "GREEN\nLIGHT",
#     xy=(550, chlorophyll[np.argmin(abs(wl - 550))]),
#     xytext=(585, 0.66),
#     fontsize=13,
#     fontweight="bold",
#     ha="center",
#     arrowprops=dict(
#         arrowstyle="->",
#         linewidth=2
#     )
# )


# # Red reflection from apple
# axes[0, 0].annotate(
#     "RED\nLIGHT",
#     xy=(650, anthocyanin[np.argmin(abs(wl - 650))]),
#     xytext=(690, 0.88),
#     fontsize=13,
#     fontweight="bold",
#     ha="center",
#     arrowprops=dict(
#         arrowstyle="->",
#         linewidth=2
#     )
# )


# # Blue reflection from jeans
# axes[0, 1].annotate(
#     "BLUE\nLIGHT",
#     xy=(455, indigo[np.argmin(abs(wl - 455))]),
#     xytext=(515, 0.78),
#     fontsize=13,
#     fontweight="bold",
#     ha="center",
#     arrowprops=dict(
#         arrowstyle="->",
#         linewidth=2
#     )
# )


# # Melanin annotation
# axes[1, 1].text(
#     0.54,
#     0.72,
#     "absorbs many\nwavelengths",
#     transform=axes[1, 1].transAxes,
#     fontsize=13,
#     fontweight="bold",
#     ha="center"
# )


# ============================================================
# MAIN TITLE
# ============================================================

# fig.suptitle(
#     "WHY DO OBJECTS HAVE COLOR?",
#     fontsize=30,
#     fontweight="bold",
#     y=0.99
# )

# fig.text(
#     0.5,
#     0.945,
#     "The wavelengths an object reflects determine the color we see",
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
    "pigments1.pdf",
    bbox_inches="tight"
)

plt.savefig(
    "pigments1.png",
    dpi=300,
    bbox_inches="tight"
)

# Colors above ~700 nm are illustrative, not visible red light.
# Spectra describe simplified objects, not isolated pigment measurements.
# plt.show()