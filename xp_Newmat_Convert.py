import os
from tkinter import Tk, filedialog, messagebox, Toplevel, Label, Button, StringVar, Radiobutton
from PIL import Image
import numpy as np

def get_resize_choice():
    root = Tk()
    root.withdraw()
    top = Toplevel(root)
    top.title("MAT Resolution")
    Label(top, text="Save _MAT.png at which resolution?").pack(padx=12, pady=8)
    choice = StringVar(value="full")
    for txt, val in [("Full", "full"), ("Half", "half"), ("Quarter", "quarter")]:
        Radiobutton(top, text=txt, variable=choice, value=val).pack(anchor="w", padx=20)
    def done():
        top.quit()
        top.destroy()
    Button(top, text="OK", command=done).pack(pady=10)
    top.protocol("WM_DELETE_WINDOW", done)
    top.mainloop()
    root.destroy()
    return choice.get()

def convert_png_channels(file_path):
    img = Image.open(file_path).convert("RGBA")
    arr = np.array(img)
    R, G, B, A = arr[:,:,0], arr[:,:,1], arr[:,:,2], arr[:,:,3]
    NRM_arr = np.zeros_like(arr)
    NRM_arr[:,:,0] = R
    NRM_arr[:,:,1] = G
    NRM_arr[:,:,2] = 0
    NRM_arr[:,:,3] = 255
    MAT_arr = np.zeros_like(arr)
    MAT_arr[:,:,0] = B
    MAT_arr[:,:,1] = A
    MAT_arr[:,:,2] = 0
    MAT_arr[:,:,3] = 255

    basefile = os.path.basename(file_path)
    base, ext = os.path.splitext(basefile)
    if "_" in base:
        rootname = base[:base.rfind("_")]
    else:
        rootname = base
    out_nrm = os.path.join(os.path.dirname(file_path), rootname + "_NRM.png")
    out_mat = os.path.join(os.path.dirname(file_path), rootname + "_MAT.png")

    Image.fromarray(NRM_arr).save(out_nrm)

    scale_choice = get_resize_choice()
    scale_factor = {"full": 1.0, "half": 0.5, "quarter": 0.25}[scale_choice]
    mat_img = Image.fromarray(MAT_arr)
    if scale_factor < 1.0:
        new_size = (
            int(mat_img.width * scale_factor),
            int(mat_img.height * scale_factor)
        )
        mat_img = mat_img.resize(new_size, Image.LANCZOS)
    mat_img.save(out_mat)

    return rootname, basefile, os.path.basename(out_nrm), os.path.basename(out_mat)

def replace_obj_texture_lines(obj_path, original_png_name, nrm_name, mat_name):
    with open(obj_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    replaced = False
    for line in lines:
        if (line.strip().startswith("TEXTURE_NORMAL")
            and original_png_name in line):
            new_lines.append(f"TEXTURE_MAP normal {nrm_name}\n")
            new_lines.append(f"TEXTURE_MAP material_gloss {mat_name}\n")
            replaced = True
        else:
            new_lines.append(line)

    if replaced:
        with open(obj_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        messagebox.showinfo("Done", f"OBJ updated!\n\n{os.path.basename(obj_path)}")
    else:
        messagebox.showwarning("Warning", f"No TEXTURE_NORMAL line with {original_png_name} found in:\n{os.path.basename(obj_path)}")

def main():
    root = Tk()
    root.withdraw()
    messagebox.showinfo("PNG Channel Splitter", "Select a PNG file to split channels.")

    file_path = filedialog.askopenfilename(
        title="Select PNG File",
        filetypes=[("PNG Files", "*.png")]
    )
    if not file_path:
        print("No file selected.")
        return

    rootname, orig_png_name, nrm_name, mat_name = convert_png_channels(file_path)
    messagebox.showinfo("Done", f"Saved:\n{nrm_name} (full res)\n{mat_name}")

    # Ask if user wants to patch an OBJ
    answer = messagebox.askyesno(
        "Update OBJ?",
        "Do you want to update an .obj file with the new texture lines?"
    )
    if not answer:
        print("OBJ update cancelled by user.")
        return

    messagebox.showinfo("Update OBJ", "Select the OBJ file to update its texture lines.")
    obj_path = filedialog.askopenfilename(
        title="Select OBJ File",
        filetypes=[("X-Plane OBJ Files", "*.obj"), ("Text Files", "*.txt"), ("All Files", "*.*")]
    )
    if not obj_path:
        print("No OBJ selected.")
        return

    replace_obj_texture_lines(obj_path, orig_png_name, nrm_name, mat_name)

if __name__ == "__main__":
    main()
