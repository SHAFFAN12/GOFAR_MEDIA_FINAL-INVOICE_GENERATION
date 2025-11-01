from fpdf import FPDF
from .base_template import BaseTemplate
from typing import Dict, Any
from datetime import datetime

class LetterTemplate(BaseTemplate):
    @property
    def template_type(self) -> str:
        return "Request Letter"

    def get_template(self) -> Dict[str, Any]:
        return {
            "type": self.template_type,
            "header_fields": [
                ("Date", "date"),
                ("Designation", "text"),
                ("Company Name", "text"),
                ("Subject", "text"),
                ("Signatories (comma separated)", "text")  # 👈 new field
            ],
            "content": {
                "paragraphs": [
                    "This is regarding the payment adjustment for the campaign.",
                    "Kindly process the request at the earliest."
                ]
            }
        }


    def validate_data(self, data: Dict[str, Any]) -> bool:
        required = ["Designation", "Company Name", "Subject", "content", "Signatories (comma separated)"]
        return all(data.get(field) for field in required)


    def generate_pdf_content(self, pdf: FPDF, data: Dict[str, Any]) -> None:
        pdf.set_left_margin(15)
        pdf.set_right_margin(15)
        
        # Date
        if "Date" in data:
            try:
                date_obj = datetime.strptime(data["Date"], "%Y-%m-%d")
                formatted_date = date_obj.strftime("%d %B %Y")
            except Exception:
                formatted_date = data["Date"]
            
            pdf.set_font("Arial", 'BU', 10)
            pdf.cell(0, 8, formatted_date, 0, 1, 'R')
            pdf.ln(5)

        # To, Designation, Company
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(0, 8, "To,", 0, 1)
        pdf.set_font("Arial", '', 10)

        designation = data.get("Designation", "")
        company = data.get("Company Name", "")

        if designation:
            pdf.cell(0, 8, f"{designation},", 0, 1)
        if company:
            pdf.cell(0, 8, f"{company},", 0, 1)

        pdf.ln(5)

        # Subject
        pdf.set_font("Arial", 'BU', 10)
        pdf.cell(0, 8, f"Subject: {data.get('Subject', '')}", 0, 1, 'L')
        pdf.ln(10)
        
        # Body Content
        pdf.set_font("Arial", '', 11)
        for para in data.get("content", "").split("\n"):
            pdf.multi_cell(0, 6, para.strip())
            pdf.ln(2)

        # Names row
        # Names row (dynamic)
        signatories = data.get("Signatories (comma separated)", "")
        if signatories:
            names = [name.strip() for name in signatories.split(",") if name.strip()]
            pdf.ln(20)
            pdf.set_font("Arial", 'B', 12)

            for i, name in enumerate(names):
                if i < len(names) - 1:
                    pdf.cell(60, 8, name, 0, 0, 'L')
                else:
                    pdf.cell(0, 8, name, 0, 1, 'L')

        
def get_template_class():
    return LetterTemplate()
