# Pigment structures

The JSON files contain PubChem PUG REST isomeric SMILES responses, downloaded
2026-09-25. The chlorophyll SDF includes PubChem's 2D coordinates.

| Panel | Depiction | PubChem CID |
|---|---|---|
| Anthocyanin | Cyanidin 3-galactoside cation (chloride counterion omitted) | [176457](https://pubchem.ncbi.nlm.nih.gov/compound/176457) |
| Indigo | Indigo (conventional trans-diketo form; depiction from [HMDB0240742](https://hmdb.ca/metabolites/HMDB0240742)) | [10215](https://pubchem.ncbi.nlm.nih.gov/compound/10215) |
| Chlorophyll | Chlorophyll a | [12085802](https://pubchem.ncbi.nlm.nih.gov/compound/12085802) |
| Betanin | Betanin | [6540685](https://pubchem.ncbi.nlm.nih.gov/compound/6540685) |
| Xanthophyll | Lutein | [5281243](https://pubchem.ncbi.nlm.nih.gov/compound/5281243) |
| Beta-carotene | Beta-carotene | [5280489](https://pubchem.ncbi.nlm.nih.gov/compound/5280489) |
| Melanin | DHI and DHICA building blocks | [114683](https://pubchem.ncbi.nlm.nih.gov/compound/114683), [119405](https://pubchem.ncbi.nlm.nih.gov/compound/119405) |

Melanin has no single molecular structure. The panel shows two eumelanin
building blocks rather than implying that either is the complete pigment.
See https://doi.org/10.1039/D0CC04702C.

`generate_molecules.py` creates transparent high-resolution PNGs and editable
SVGs with RDKit. Install RDKit only to regenerate these assets:

```
python3 -m pip install rdkit
python3 generate_molecules.py
```

The four figure scripts use the saved PNGs via `pigment_molecules.py`, so they
require only their existing NumPy, Matplotlib and Pillow dependencies. Keep
this folder and the shared helper next to the plotting scripts. To reposition
or resize insets, edit `BOXES` in `pigment_molecules.py` (axes-relative units).

Structures represent particular molecular forms; protonation, tautomerism,
and the chemical environment can change a pigment's spectrum. They are not
quantitative models for the illustrative reflectance curves.
