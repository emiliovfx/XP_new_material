# X-Plane PNG Channel Splitter & OBJ Patch Tool

This script lets you:

- Extract channels from a PNG texture (`R` & `G` to `_NRM.png`, `B` & `A` to `_MAT.png`)
- Optionally patch a text-format X-Plane 8 OBJ file to reference the new textures

## Requirements

- Python 3.7+ (with Tkinter)
- Pillow
- Numpy

## Instructions

- Download the xp_Newmat_Convert.py
- Run using py xp_Mawmat_Convert.py in a command window.
- Select a PNG file when prompted.
- Choose the desired resolution for `_MAT.png`.
  this can be FULL to preserve the original size, half or quarter.
  By rescaling the MAT texture you will save VRAM.   The rescaling works in power of 2 rescaling.
  I.E. If your original texture is 4096 x 4096, it will be rescaled to 2048 x 2048 by half
  and to 1024 x 1024 by quarter resolution.

- 
- Choose whether to patch an `.obj` file.
- Select the `.obj` file if you opt to patch.
- Your new textures and/or updated OBJ will be saved in the same folder.

## Notes

- The script automatically renames outputs, e.g. `Interior_2B_NML.png` becomes `Interior_2B_NRM.png` and `Interior_2B_MAT.png`.
- Only the `TEXTURE_NORMAL ...` line is replaced in the OBJ, and the rest of the file is preserved.

Tested on Windows with Python 3.10.
