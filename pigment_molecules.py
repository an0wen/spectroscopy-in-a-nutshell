"""Shared molecule insets for the English and Spanish outreach figures.

Edit BOXES (axes fractions: left, bottom, width, height) to move/resize them.
Images are generated from local PubChem records by generate_molecules.py.
"""
from pathlib import Path
import matplotlib.pyplot as plt

ASSETS = Path(__file__).resolve().parent / 'molecule_assets'
BOXES = {
    'apple': (0.01, 0.30, 0.57, 0.67),
    'jeans': (0.39, 0.36, 0.59, 0.58),
    'leaf': (0.03, 0.50, 0.93, 0.48),
    'beet': (0.01, 0.30, 0.58, 0.68),
    'yellow_leaf': (0.05, 0.80, 0.92, 0.20),
    'carrot': (0.05, 0.80, 0.92, 0.20),
    'eye': (0.12, 0.52, 0.82, 0.45),
}
KEYS = {'apple': 'anthocyanin', 'jeans': 'indigo', 'leaf': 'chlorophyll',
        'beet': 'betanin', 'yellow_leaf': 'xanthophyll', 'carrot': 'beta_carotene'}
LABELS = {
    'apple': ('Cyanidin 3-galactoside', 'Cianidina 3-galactósido'),
    'leaf': ('Chlorophyll a', 'Clorofila a'),
    'yellow_leaf': ('Lutein', 'Luteína'),
    'eye': ('Eumelanin building blocks', 'Unidades de la eumelanina'),
}


def add_molecule(ax, icon, language='en'):
    left, bottom, width, height = BOXES[icon]
    spanish = language == 'es'
    caption = LABELS.get(icon, ('', ''))[int(spanish)]
    caption_height = 0.06 if caption else 0

    def picture(key, bounds):
        inset = ax.inset_axes(bounds, zorder=15)
        inset.imshow(plt.imread(ASSETS / f'{key}.png'), interpolation='antialiased')
        inset.set_axis_off()
        inset.patch.set_alpha(0)

    if icon == 'eye':
        # Melanin has no unique molecular structure. Show two precursors,
        # explicitly labeled as building blocks, not a fictitious monomer.
        for key, dx in [('dhi', 0), ('dhica', width / 2)]:
            picture(key, (left + dx, bottom + 0.11, width / 2, height - 0.11))
            ax.text(left + dx + width / 4, bottom + 0.075, key.upper(),
                    transform=ax.transAxes, ha='center', va='center',
                    fontsize=10, color='#454545')
    else:
        picture(KEYS[icon], (left, bottom + caption_height, width,
                            height - caption_height))
    if caption:
        ax.text(left + width / 2, bottom + 0.015, caption,
                transform=ax.transAxes, ha='center', va='bottom',
                fontsize=10, color='#454545')
