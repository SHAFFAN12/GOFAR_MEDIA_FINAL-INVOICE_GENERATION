import customtkinter as ctk
from tkinter import filedialog, messagebox
from tkcalendar import DateEntry
from datetime import datetime
from document_manager import DocumentManager
from signer import PDFSignatureApp
from utils import get_output_dir
from pathlib import Path
import json

ctk.set_appearance_mode("System")  # "Dark", "Light", or "System"
ctk.set_default_color_theme("blue")  # Options: "blue", "dark-blue", "green"

class DocumentApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🧾 Document Generator")
        self.geometry("900x700")
        self.minsize(850, 600)

        self.doc_manager = DocumentManager()
        self.entry_widgets = {}
        self.line_item_entries = []
        self.error_labels = {}
        self.earnings_entries = []

        self._setup_ui()

    def _setup_ui(self):
        # -------- Sidebar for Selections --------
        sidebar = ctk.CTkFrame(self, corner_radius=15)
        sidebar.pack(side="left", fill="y", padx=10, pady=10)

        ctk.CTkLabel(sidebar, text="⚙️ Settings", font=("Helvetica", 18, "bold")).pack(pady=(15, 20))

        # Company dropdown
        self.company_var = ctk.StringVar()
        ctk.CTkLabel(sidebar, text="Select Company:", anchor="w").pack(pady=(0, 5))
        self.company_menu = ctk.CTkOptionMenu(sidebar, variable=self.company_var,
                                              values=["GoFar Media", "Glory Enterprises"])
        self.company_menu.pack(fill="x", pady=(0, 15))
        self.company_var.set("GoFar Media")

        # Document type dropdown
        self.doc_type_var = ctk.StringVar()
        ctk.CTkLabel(sidebar, text="Document Type:", anchor="w").pack(pady=(0, 5))
        self.doc_type_menu = ctk.CTkOptionMenu(
            sidebar, variable=self.doc_type_var,
            values=list(self.doc_manager.templates.keys()),
            command=lambda _: self.load_form_fields()
        )
        self.doc_type_menu.pack(fill="x", pady=(0, 20))

        # Buttons
        ctk.CTkButton(sidebar, text="🧾 Generate Document", command=self.generate_document, width=180).pack(pady=10)
        ctk.CTkButton(sidebar, text="📂 Load & Edit", command=self.load_document_for_edit, width=180).pack(pady=5)

        # -------- Main Content (Scrollable Form) --------
        main_frame = ctk.CTkFrame(self, corner_radius=15)
        main_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.canvas = ctk.CTkCanvas(main_frame, highlightthickness=0)
        self.scroll_frame = ctk.CTkFrame(self.canvas)
        self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        scrollbar = ctk.CTkScrollbar(main_frame, orientation="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    # ---------- FORM BUILDING ----------
    def load_form_fields(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        self.entry_widgets.clear()
        self.line_item_entries.clear()
        self.earnings_entries.clear()

        doc_type = self.doc_type_var.get()
        template = self.doc_manager.templates.get(doc_type, {})

        ctk.CTkLabel(self.scroll_frame, text=f"{doc_type} Form",
                     font=("Helvetica", 20, "bold")).pack(pady=(10, 15))

        for field, field_type in template.get("header_fields", []):
            self._add_form_field(field, field_type)

        if doc_type in ["Invoice", "Sales Tax Invoice"]:
            self._add_line_items_section(template)
        elif doc_type == "Request Letter":
            self._add_letter_content_field()
        elif doc_type == "Salary Slip":
            self._add_salary_slip_sections(template)

    def _add_form_field(self, field, field_type):
        frame = ctk.CTkFrame(self.scroll_frame, corner_radius=10)
        frame.pack(fill="x", pady=5, padx=15)

        ctk.CTkLabel(frame, text=field + ":", width=180, anchor="w").pack(side="left", padx=10, pady=5)

        if field_type == "date":
            entry = DateEntry(frame, date_pattern='dd-mm-yyyy')
        else:
            entry = ctk.CTkEntry(frame, width=300, placeholder_text=f"Enter {field}")

        entry.pack(side="left", padx=5, pady=5)
        self.entry_widgets[field] = entry

    def _add_salary_slip_sections(self, template):
        ctk.CTkLabel(self.scroll_frame, text="💰 Earnings", font=("Helvetica", 16, "bold")).pack(pady=(15, 5))
        for item in template.get("earnings_inputs", []):
            self._add_salary_item(item)

    def _add_salary_item(self, item):
        frame = ctk.CTkFrame(self.scroll_frame, corner_radius=8)
        frame.pack(fill="x", pady=3, padx=15)

        name = item["name"]
        ctk.CTkLabel(frame, text=name + ":", width=200, anchor="w").pack(side="left", padx=10)
        entry = ctk.CTkEntry(frame, width=120)
        entry.insert(0, "0")
        entry.pack(side="left", padx=5)
        self.earnings_entries.append((name, entry))

    def _add_letter_content_field(self):
        ctk.CTkLabel(self.scroll_frame, text="✉️ Letter Content", font=("Helvetica", 16, "bold")).pack(pady=(15, 5))
        self.content_text = ctk.CTkTextbox(self.scroll_frame, width=700, height=300)
        self.content_text.pack(padx=15, pady=10, fill="both", expand=True)

    def _add_line_items_section(self, template):
        ctk.CTkLabel(self.scroll_frame, text="📦 Line Items", font=("Helvetica", 16, "bold")).pack(pady=(15, 5))
        self.items_container = ctk.CTkFrame(self.scroll_frame, corner_radius=10)
        self.items_container.pack(fill="x", padx=15, pady=5)
        self._add_line_item_row(template)

        ctk.CTkButton(self.scroll_frame, text="+ Add Item", command=lambda: self._add_line_item_row(template)).pack(pady=8)

    def _add_line_item_row(self, template):
        row = ctk.CTkFrame(self.items_container, corner_radius=5)
        row.pack(fill="x", pady=2, padx=5)

        entry_list = []
        for col in template["line_items"]["columns"]:
            # Detect columns containing "date"
            if "date" in col.lower():
                entry = DateEntry(row, date_pattern='dd-mm-yyyy', width=12)
            else:
                entry = ctk.CTkEntry(row, width=120, placeholder_text=col)

            entry.pack(side="left", padx=3, pady=3)
            entry_list.append(entry)

        remove_btn = ctk.CTkButton(
            row, text="✕", width=30,
            fg_color="red", hover_color="#a33",
            command=lambda: self._remove_line_item_row(row, entry_list)
        )
        remove_btn.pack(side="left", padx=5)

        self.line_item_entries.append(entry_list)


    def _remove_line_item_row(self, frame, entry_list):
        frame.destroy()
        self.line_item_entries.remove(entry_list)

    # ---------- DATA COLLECTION ----------
    def collect_form_data(self):
        doc_type = self.doc_type_var.get()
        template = self.doc_manager.templates.get(doc_type, {})
        data = {}
        for field, _ in template.get("header_fields", []):
            widget = self.entry_widgets[field]
            if isinstance(widget, DateEntry):
                data[field] = widget.get_date().strftime("%d-%m-%Y")
            else:
                data[field] = widget.get().strip()
        if doc_type == "Salary Slip":
            for name, entry in self.earnings_entries:
                data[name] = entry.get().strip()
        if doc_type == "Request Letter":
            data["content"] = self.content_text.get("1.0", "end").strip()
        if doc_type in ["Invoice", "Sales Tax Invoice"]:
            columns = template["line_items"]["columns"]
            data["line_items"] = []
            for entry_row in self.line_item_entries:
                row = {col: entry_row[i].get().strip() for i, col in enumerate(columns)}
                if any(row.values()):
                    data["line_items"].append(row)
        return data

    # ---------- GENERATE DOCUMENT ----------
    def generate_document(self):
        try:
            doc_type = self.doc_type_var.get()
            company = self.company_var.get()
            if not doc_type or not company:
                messagebox.showwarning("Missing Data", "Please select both company and document type.")
                return

            data = self.collect_form_data()
            valid = self.doc_manager.templates[doc_type]["template_class"].validate_data(data)
            if not valid:
                messagebox.showerror("Validation Error", "Some required fields are missing.")
                return

            filepath = self.doc_manager.generate_document(company=company, doc_type=doc_type, data=data)
            if messagebox.askyesno("Success", f"Document generated successfully!\n{filepath}\n\nAdd signature?"):
                PDFSignatureApp(ctk.CTkToplevel(self), filepath)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---------- LOAD EXISTING DOCUMENT ----------
    def load_document_for_edit(self):
        try:
            filepath = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
            if not filepath:
                return

            json_path = Path(filepath).with_suffix(".json")
            if not json_path.exists():
                messagebox.showerror("Error", "No editable data found for this document.")
                return

            with open(json_path, "r") as f:
                saved_data = json.load(f)
            self.populate_form_with_data(saved_data)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def populate_form_with_data(self, saved_data):
        company = saved_data.get("company")
        doc_type = saved_data.get("doc_type")
        form_data = saved_data.get("form_data", {})

        self.company_var.set(company)
        self.doc_type_var.set(doc_type)
        self.load_form_fields()

        for field, widget in self.entry_widgets.items():
            val = form_data.get(field, "")
            if isinstance(widget, DateEntry):
                try:
                    widget.set_date(datetime.strptime(val, "%d-%m-%Y"))
                except:
                    pass
            else:
                widget.delete(0, "end")
                widget.insert(0, str(val))

        if doc_type == "Request Letter":
            self.content_text.delete("1.0", "end")
            self.content_text.insert("1.0", form_data.get("content", ""))
        elif doc_type in ["Invoice", "Sales Tax Invoice"]:
            template = self.doc_manager.templates.get(doc_type, {})
            for child in self.items_container.winfo_children():
                child.destroy()
            self.line_item_entries.clear()
            for item in form_data.get("line_items", []):
                self._add_line_item_row(template)
                for i, (col, val) in enumerate(item.items()):
                    self.line_item_entries[-1][i].insert(0, val)
        elif doc_type == "Salary Slip":
            for name, entry in self.earnings_entries:
                entry.delete(0, "end")
                entry.insert(0, form_data.get(name, "0"))

if __name__ == "__main__":
    app = DocumentApp()
    app.mainloop()
