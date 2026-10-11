"""Regenerate local structure images: python -m pip install rdkit; python generate_molecules.py.

PubChem source records are saved in molecule_assets; no network is needed.
Normal figure generation uses the saved PNGs and does not require RDKit.
"""
import json
from pathlib import Path
from rdkit import Chem
from rdkit.Chem import rdDepictor, rdMolDescriptors
from rdkit.Chem.Draw import rdMolDraw2D
from PIL import Image
from io import BytesIO

ASSETS = Path(__file__).resolve().parent / 'molecule_assets'


def molecule(key):
    record = json.loads((ASSETS / f'{key}.json').read_text())['PropertyTable']['Properties'][0]
    mol = Chem.MolFromSmiles(record['SMILES'])
    if key == 'anthocyanin':
        # Remove chloride counterion; depict the colored flavylium cation.
        mol = max(Chem.GetMolFrags(mol, asMols=True), key=lambda m: m.GetNumAtoms())
    if key == 'indigo':
        # PubChem returns an enol tautomer; use the conventional diketo form.
        # Conventional trans-indigo structure from HMDB0240742.
        # https://hmdb.ca/metabolites/HMDB0240742
        mol = Chem.MolFromSmiles(r'O=C1\C(NC2=CC=CC=C12)=C1/NC2=CC=CC=C2C1=O')
    if key == 'chlorophyll':
        # Preserve the database layout, including magnesium in the ring center.
        mol = Chem.MolFromMolFile(str(ASSETS / 'chlorophyll.sdf'), removeHs=True)
    else:
        rdDepictor.Compute2DCoords(mol)
        rdDepictor.NormalizeDepiction(mol)
    assert mol is not None, key
    return mol


def draw(key, mol, width=1800, height=950):
    for fmt in ('png', 'svg'):
        drawer = (rdMolDraw2D.MolDraw2DCairo(width, height) if fmt == 'png'
                  else rdMolDraw2D.MolDraw2DSVG(width, height))
        options = drawer.drawOptions()
        options.clearBackground = False
        options.useBWAtomPalette()
        options.bondLineWidth = 6
        options.minFontSize = 28
        options.maxFontSize = 60
        options.padding = 0.06
        rdMolDraw2D.PrepareAndDrawMolecule(drawer, mol)
        drawer.FinishDrawing()
        output = drawer.GetDrawingText()
        path = ASSETS / f'{key}.{fmt}'
        if fmt == 'png':
            im = Image.open(BytesIO(output)).convert('RGBA')
            bounds = im.getchannel('A').getbbox()
            if bounds:
                x0, y0, x1, y1 = bounds
                pad = 25
                im = im.crop((max(0, x0-pad), max(0, y0-pad),
                              min(im.width, x1+pad), min(im.height, y1+pad)))
            im.save(path)
        else:
            path.write_text(output)


if __name__ == '__main__':
    for key in ['anthocyanin', 'indigo', 'chlorophyll', 'betanin',
                'xanthophyll', 'beta_carotene', 'dhi', 'dhica']:
        mol = molecule(key)
        draw(key, mol, height=430 if key in ('xanthophyll', 'beta_carotene') else 950)
        print(key, rdMolDescriptors.CalcMolFormula(mol))
