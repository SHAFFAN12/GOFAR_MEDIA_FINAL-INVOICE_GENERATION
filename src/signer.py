import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, Menu
from PIL import Image, ImageTk
from pdf2image import convert_from_path
import fitz  # PyMuPDF
import os
import tempfile
import sys
from pathlib import Path

def get_poppler_path():
    if hasattr(sys, "_MEIPASS"):  # PyInstaller ke liye
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).parent.parent
    return str(base_path / "poppler" / "bin")

POPPLER_PATH = get_poppler_path()

A4_WIDTH_PX = 794
A4_HEIGHT_PX = 1123

class PDFSignatureApp:
    def __init__(self, root, pdf_path=None):
        self.root = root
        self.root.title("PDF Signature Tool")
        self.pdf_path = pdf_path
        self.zoom_factor = 1.0
        self.signature_items = []
        self.selected_item = None
        self.dragging = False

        self.canvas_frame = tk.Frame(root)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.canvas_frame, bg="white", scrollregion=(0, 0, A4_WIDTH_PX, A4_HEIGHT_PX), cursor="arrow")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scroll_y = tk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.configure(yscrollcommand=self.scroll_y.set)

        btn_frame = tk.Frame(root)
        btn_frame.pack(fill=tk.X, pady=5)

        tk.Button(btn_frame, text="Zoom In", command=self.zoom_in).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Zoom Out", command=self.zoom_out).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Add Signature/Stamp", command=self.add_image).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Save PDF", command=self.save_pdf).pack(side=tk.LEFT, padx=5)

        self.root.bind("<Delete>", self.delete_selected)

        if self.pdf_path:
            self.load_pdf(self.pdf_path)

    def load_pdf(self, path):
        self.pdf_path = path
        self.original_pdf_img = convert_from_path(path, poppler_path=POPPLER_PATH)[0]
        self.render_pdf()

    def render_pdf(self):
        img = self.original_pdf_img.copy()
        w, h = int(A4_WIDTH_PX * self.zoom_factor), int(A4_HEIGHT_PX * self.zoom_factor)
        img = img.resize((w, h))
        self.pdf_img = img
        self.tk_pdf = ImageTk.PhotoImage(img)

        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_pdf)

        for item in self.signature_items:
            self.place_on_canvas(item)

        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def zoom_in(self):
        self.zoom_factor += 0.1
        self.render_pdf()

    def zoom_out(self):
        if self.zoom_factor > 0.3:
            self.zoom_factor -= 0.1
            self.render_pdf()

    def add_image(self):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if not path:
            return
        pil_img = Image.open(path).convert("RGBA")
        item = {
            "path": path,
            "image": pil_img,
            "rotation": 0,
            "x": 100,
            "y": 100,
            "canvas_x_px": 100 * self.zoom_factor,
            "canvas_y_px": 100 * self.zoom_factor,
            "width": pil_img.width,
            "height": pil_img.height,
            "id": None
        }
        self.signature_items.append(item)
        self.place_on_canvas(item)

    def place_on_canvas(self, item):
        img = item["image"].rotate(item["rotation"], expand=True)
        img = img.resize(
            (int(item["width"] * self.zoom_factor), int(item["height"] * self.zoom_factor))
        )
        item["tk_img"] = ImageTk.PhotoImage(img)

        x = int(item["x"] * self.zoom_factor)
        y = int(item["y"] * self.zoom_factor)
        item["canvas_x_px"] = x
        item["canvas_y_px"] = y

        if item.get("id"):
            self.canvas.delete(item["id"])

        item["id"] = self.canvas.create_image(x, y, anchor="nw", image=item["tk_img"])

        self.canvas.tag_bind(item["id"], "<ButtonPress-1>", lambda e, i=item: self.start_drag(e, i))
        self.canvas.tag_bind(item["id"], "<B1-Motion>", lambda e, i=item: self.drag(e, i))
        self.canvas.tag_bind(item["id"], "<ButtonRelease-1>", lambda e, i=item: self.stop_drag(e, i))
        self.canvas.tag_bind(item["id"], "<Button-3>", lambda e, i=item: self.show_context_menu(e, i))

    def start_drag(self, event, item):
        self.selected_item = item
        self.dragging = True
        self.canvas.config(cursor="fleur")
        item["drag_start"] = (event.x, event.y)

    def drag(self, event, item):
        if not self.dragging:
            return
        dx = event.x - item["drag_start"][0]
        dy = event.y - item["drag_start"][1]
        self.canvas.move(item["id"], dx, dy)
        item["drag_start"] = (event.x, event.y)

    def stop_drag(self, event, item):
        coords = self.canvas.coords(item["id"])
        item["canvas_x_px"] = coords[0]
        item["canvas_y_px"] = coords[1]
        # item["x"] = coords[0] / self.zoom_factor
        # item["y"] = coords[1] / self.zoom_factor
        self.canvas.config(cursor="arrow")
        self.dragging = False

    def show_context_menu(self, event, item):
        self.selected_item = item
        menu = Menu(self.root, tearoff=0)
        menu.add_command(label="Resize", command=lambda: self.resize(item))
        menu.add_command(label="Rotate", command=lambda: self.rotate(item))
        menu.add_command(label="Delete", command=lambda: self.delete_item(item))
        menu.post(event.x_root, event.y_root)

    def resize(self, item):
        new_width = simpledialog.askinteger("Resize", "Enter new width (px):", initialvalue=item["width"])
        if new_width:
            ratio = new_width / item["width"]
            item["width"] = new_width
            item["height"] = int(item["height"] * ratio)
            self.render_pdf()

    def rotate(self, item):
        item["rotation"] = (item["rotation"] + 45) % 360
        self.render_pdf()

    def delete_item(self, item):
        if item in self.signature_items:
            self.signature_items.remove(item)
        self.render_pdf()

    def delete_selected(self, event=None):
        if self.selected_item:
            self.delete_item(self.selected_item)
            self.selected_item = None

    def save_pdf(self):
        if not self.pdf_path:
            messagebox.showerror("Error", "Please open a PDF file first.")
            return

        doc = fitz.open(self.pdf_path)
        page = doc[0]

        # PDF size in points (72 DPI)
        pdf_width_pt = page.rect.width
        pdf_height_pt = page.rect.height

        # Canvas/rendered image size in pixels (after zoom)
        canvas_width = self.pdf_img.width
        canvas_height = self.pdf_img.height

        # Scale factors: canvas px → PDF points
        scale_x = pdf_width_pt / canvas_width
        scale_y = pdf_height_pt / canvas_height

        # ✅ If there are any signature/stamp items, add them — else skip silently
        for item in getattr(self, "signature_items", []):
            try:
                rotated_img = item["image"].rotate(item["rotation"], expand=True)

                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
                    temp_path = temp_file.name
                    rotated_img.save(temp_path, format="PNG")

                # Get canvas coordinates in pixels
                x_canvas = item["canvas_x_px"]
                y_canvas = item["canvas_y_px"]

                # Get width & height on canvas (in pixels), accounting for zoom
                w = item["width"] * self.zoom_factor
                h = item["height"] * self.zoom_factor

                # Convert to PDF points
                x_pt = x_canvas * scale_x
                y_pt = y_canvas * scale_y
                w_pt = w * scale_x
                h_pt = h * scale_y

                rect = fitz.Rect(x_pt, y_pt, x_pt + w_pt, y_pt + h_pt)
                page.insert_image(rect, filename=temp_path)

                os.unlink(temp_path)

            except Exception:
                pass  # Silently skip any image errors

        # ✅ Always allow saving, even if no images were added
        save_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Save PDF As"
        )

        if save_path:
            doc.save(save_path)
            doc.close()
            messagebox.showinfo("Success", f"PDF saved to:\n{save_path}")
