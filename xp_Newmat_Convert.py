import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import numpy as np

def convert_png_channels(file_path, scale_choice):
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

def gui_main():
    root = tk.Tk()
    root.title("X-Plane PNG Channel Splitter")

    file_var = tk.StringVar()
    scale_choice = tk.StringVar(value="full")

    def browse_file():
        fname = filedialog.askopenfilename(
            title="Select PNG File",
            filetypes=[("PNG Files", "*.png")]
        )
        if fname:
            file_var.set(fname)

    def do_convert():
        file_path = file_var.get()
        if not file_path:
            messagebox.showerror("Error", "No PNG file selected.")
            return
        rootname, orig_png_name, nrm_name, mat_name = convert_png_channels(file_path, scale_choice.get())
        messagebox.showinfo("Done", f"Saved:\n{nrm_name} (full res)\n{mat_name}")

        # Ask about OBJ patching
        if messagebox.askyesno("Update OBJ?", "Do you want to update an .obj file with the new texture lines?"):
            obj_path = filedialog.askopenfilename(
                title="Select OBJ File",
                filetypes=[("X-Plane OBJ Files", "*.obj"), ("Text Files", "*.txt"), ("All Files", "*.*")]
            )
            if obj_path:
                replace_obj_texture_lines(obj_path, orig_png_name, nrm_name, mat_name)
        root.quit()

    # Layout
    tk.Label(root, text="PNG File:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
    tk.Entry(root, textvariable=file_var, width=40).grid(row=0, column=1, padx=5, pady=5)
    tk.Button(root, text="Browse...", command=browse_file).grid(row=0, column=2, padx=5, pady=5)

    tk.Label(root, text="MAT.png Resolution:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
    for idx, (txt, val) in enumerate([("Full", "full"), ("Half", "half"), ("Quarter", "quarter")]):
        tk.Radiobutton(root, text=txt, variable=scale_choice, value=val).grid(row=1, column=1+idx, sticky="w", padx=3)

    tk.Button(root, text="Convert", command=do_convert, width=15).grid(row=2, column=1, columnspan=2, pady=15)

    root.mainloop()

if __name__ == "__main__":
    gui_main()
