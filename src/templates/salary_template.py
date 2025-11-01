from fpdf import FPDF
from .base_template import BaseTemplate
from typing import Dict, Any
from num2words import num2words
import locale
from datetime import datetime


class SalaryTemplate(BaseTemplate):
    @property
    def template_type(self) -> str:
        return "Salary Slip"

    def get_template(self) -> Dict[str, Any]:
        return {
            "type": self.template_type,
            "header_fields": [
                ("Employee Name", "text"),
                ("Employee No", "text"),
                ("Designation", "text"),
                ("Department", "text"),
                ("CNIC", "text"),
                ("Month", "text")
            ],
            "earnings_inputs": [
                {"name": "Basic Salary", "type": "number"},
                {"name": "Mobile Allowance", "type": "number"},
                {"name": "Fuel Allowance", "type": "number"},
                {"name": "Other Allowance", "type": "number"}
            ]
        }

    def validate_data(self, data: Dict[str, Any]) -> bool:
        required_fields = ["Employee Name", "Employee No", "Designation", "Department", "CNIC", "Month"]
        for field in required_fields:
            if not data.get(field):
                return False
        return True

    def generate_pdf_content(self, pdf: FPDF, data: Dict[str, Any]) -> None:
        try:
            locale.setlocale(locale.LC_ALL, '')
        except:
            pass

        # Date (top right, no border)
        pdf.set_font("Arial", '', 10)
        current_date = datetime.now().strftime("%d %B %Y")
        pdf.cell(0, 8, f"Date: {current_date}", 0, 1, 'R')
        pdf.ln(5)

        # Salary Slip Title with border
        month_year = data.get("Month", "")
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, f"Salary Slip for {month_year}", 1, 1, 'C')

        # Employee Information
        employee_info = [
            ("Name", data.get("Employee Name", "")),
            ("Emp. No", data.get("Employee No", "")),
            ("Designation", data.get("Designation", "")),
            ("Department", data.get("Department", "")),
            ("CNIC", data.get("CNIC", ""))
        ]

        start_x = pdf.get_x()
        start_y = pdf.get_y()
        pdf.set_font("Arial", '', 10)

        for label, value in employee_info:
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(30, 8, f"{label}:", 0, 0, 'L')
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(0, 8, value, 0, 1, 'L')

        # Draw border around employee info
        end_y = pdf.get_y()
        block_height = end_y - start_y
        pdf.set_xy(start_x, start_y)
        pdf.cell(0, block_height, "", "TLR", 1, 'L')

        # Earnings Table Header
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(120, 8, "EARNINGS", 1, 0, 'C')
        pdf.cell(60, 8, "", 1, 1, 'C')
        
        
        # Earnings Rows
        total_earnings = 0
        pdf.set_font("Arial", '', 10)

        def add_row(name, value):
            nonlocal total_earnings
            if value > 0:
                pdf.cell(60, 8, name, "L", 0, 'L')  # Label in first column (left border only)
                pdf.cell(60, 8, f"{int(value):,}", "R", 0, 'L')  # Amount in second column (right border only)
                pdf.cell(60, 8, "", "R", 1, 'L')  # Empty third column (right border only)
                total_earnings += value

        basic_salary = float(data.get("Basic Salary", "0").replace(",", "") or 0)
        add_row("Basic Salary", basic_salary)

        mobile_allowance = float(data.get("Mobile Allowance", "0").replace(",", "") or 0)
        add_row("Mobile Allowance", mobile_allowance)

        fuel_allowance = float(data.get("Fuel Allowance", "0").replace(",", "") or 0)
        add_row("Fuel Allowance", fuel_allowance)

        # Add empty row for spacing
        pdf.cell(60, 6, "", "L", 0)
        pdf.cell(60, 6, "", "R", 0)
        pdf.cell(60, 6, "", "R", 1)

        # Gross Salary
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(60, 10, "Gross Salary", "LB", 0, 'L')  # Left and bottom border
        pdf.cell(60, 10, f"{int(total_earnings):,}", "RB", 0, 'L')  # Right and bottom border
        pdf.cell(60, 10, "", "RB", 1, 'L')  # Right and bottom border

        # ⚡ Removed padding rows before Net Pay

        # Net Pay (same as Gross since no deductions)
        net_pay = total_earnings
        pdf.set_font("Arial", 'B', 12)

        # NET PAY row (center aligned text)
        pdf.cell(120, 10, "NET PAY", 1, 0, 'C')  # ← 'C' for center align
        pdf.cell(60, 10, f"{int(net_pay):,}", 1, 1, 'C')
        pdf.ln(8)


        # Amount in Words
        try:
            words = num2words(net_pay, lang='en').replace('and', '').title()
        except:
            words = f"{int(net_pay):,}"

        pdf.set_font("Arial", 'IU', 10)
        pdf.cell(0, 8, f"Amount In Words: {words} Only", 0, 1, 'L')  # ← "0" means no border
        pdf.ln(10)



def get_template_class():
    return SalaryTemplate()
