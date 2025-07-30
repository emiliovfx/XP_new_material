import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
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
        messagebox.showinfo("Done", f"OBJ updated!\n\n{os.path.basename(obj_path)}")
        with open(obj_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
    else:
        messagebox.showwarning("Warning", f"No TEXTURE_NORMAL line with {original_png_name} found in:\n{os.path.basename(obj_path)}")

def gui_main():
    root = tk.Tk()
    root.title("X-Plane PNG Channel Splitter")
    root.resizable(False, False)  # Prevent window from being stretched

    mainframe = tk.Frame(root, padx=15, pady=10)
    mainframe.pack()

    file_var = tk.StringVar()
    file_display_var = tk.StringVar(value="No file selected.")
    preview_image = [None]  # Use list to allow reassignment in nested scope

    # --- FILE PICKER SECTION WITH PREVIEW ---
    file_frame = tk.LabelFrame(mainframe, text="Select PNG Texture File", padx=10, pady=8)
    file_frame.pack(fill="x", pady=(0,10))

    tk.Entry(file_frame, textvariable=file_var, width=38).pack(side="left", fill="x", expand=True, padx=(0,6))

    preview_frame = tk.Frame(mainframe)
    preview_frame.pack()
    preview_label = tk.Label(preview_frame, image=None)
    preview_label.pack()

    def show_preview(fname):
        preview_label.config(image=None)
        preview_image[0] = None
        if fname and os.path.exists(fname):
            try:
                img = Image.open(fname)
                # Keep aspect, fit in box
                max_size = (256, 256)
                img.thumbnail(max_size, Image.LANCZOS)
                preview_image[0] = ImageTk.PhotoImage(img)
                preview_label.config(image=preview_image[0])
            except Exception:
                preview_image[0] = None

    def browse_file():
        fname = filedialog.askopenfilename(
            title="Select PNG File",
            filetypes=[("PNG Files", "*.png")]
        )
        if fname:
            file_var.set(fname)
            file_display_var.set("Selected: " + os.path.basename(fname))
            show_preview(fname)
        else:
            file_display_var.set("No file selected.")
            show_preview(None)

    tk.Button(file_frame, text="Browse...", command=browse_file, width=10).pack(side="right")
    tk.Label(file_frame, textvariable=file_display_var, fg="gray").pack(side="bottom", fill="x", pady=(6,0))

    # --- RESOLUTION SECTION ---
    scale_choice = tk.StringVar(value="full")
    res_frame = tk.LabelFrame(mainframe, text="MAT.png Resolution", padx=10, pady=8)
    res_frame.pack(fill="x", pady=(0,10))
    for idx, (txt, val) in enumerate([("Full", "full"), ("Half", "half"), ("Quarter", "quarter")]):
        tk.Radiobutton(res_frame, text=txt, variable=scale_choice, value=val).pack(side="left", padx=10, pady=2)

    # --- CONVERT BUTTON ---
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

    tk.Button(mainframe, text="Convert", command=do_convert, width=18, height=2).pack(pady=12)

    root.mainloop()

if __name__ == "__main__":
    gui_main()
