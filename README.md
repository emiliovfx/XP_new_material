# X-Plane PNG Channel Splitter & OBJ Patch Tool

This script lets you:

- Extract channels from a PNG texture (`R` & `G` to `_NRM.png`, `B` & `A` to `_MAT.png`)
- Optionally patch a text-format X-Plane 8 OBJ file to reference the new textures

## Requirements

- Python 3.7+ (with Tkinter)
- Pillow
- Numpy

## Instructions

- Select a PNG file when prompted.
- Choose the desired resolution for `_MAT.png`.
- Choose whether to patch an `.obj` file.
- Select the `.obj` file if you opt to patch.
- Your new textures and/or updated OBJ will be saved in the same folder.

## Notes

- The script automatically renames outputs, e.g. `Interior_2B_NML.png` becomes `Interior_2B_NRM.png` and `Interior_2B_MAT.png`.
- Only the `TEXTURE_NORMAL ...` line is replaced in the OBJ, and the rest of the file is preserved.

Tested on Windows with Python 3.10.
