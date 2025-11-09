from fpdf import FPDF
from .base_template import BaseTemplate
from typing import Dict, Any, List
from num2words import num2words
import locale


class InvoiceTemplate(BaseTemplate):
    @property
    def template_type(self) -> str:
        return "Invoice"

    def get_template(self) -> Dict[str, Any]:
        return {
            "type": self.template_type,
            "header_fields": [
                ("Custom Title (Optional)", "text"),
                ("M/s", "text"),
                ("Campaign", "text"),
                ("Date", "date"),
                ("Invoice No", "readonly"),
                ("Invoice Month", "text")
            ],
            "line_items": {
                "columns": [
                    "Description",
                    "Campaign Start Date",
                    "Campaign End Date",
                    "Size",
                    "Duration",
                    "Amount"
                ]
            },
            "footer": {
                "total": True,
                "amount_in_words": True
            }
        }

    def validate_data(self, data: Dict[str, Any]) -> (bool, str):
        # Invoice No is now auto-generated, so it's not required in the form data validation
        required = ["M/s", "Campaign", "Date", "Invoice Month"]
        for field in required:
            if not data.get(field):
                return False, f"'{field}' is a required field."

        if not data.get("line_items"):
             return False, "Please add at least one line item to the invoice."
        
        if not isinstance(data.get("line_items"), list):
            return False, "Line items data is corrupted."
            
        # Validate that all required columns are present in each line item
        for i, item in enumerate(data["line_items"]):
            for col in self.get_template()["line_items"]["columns"]:
                if not item.get(col):
                    return False, f"Missing value for '{col}' in line item #{i+1}."
        return True, ""

    def generate_pdf_content(self, pdf: FPDF, data: Dict[str, Any]) -> None:
        pdf.set_font("Arial", 'B', 16)
        title = (data.get("Custom Title (Optional)") or self.template_type).upper()
        pdf.cell(0, 10, title, 0, 1, 'C')
        pdf.set_draw_color(0, 0, 0)
        pdf.set_line_width(0.4)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)

        self._add_header_fields(pdf, data)
        self._add_line_items(pdf, data["line_items"])
        self._add_totals_and_footer(pdf, data["line_items"])

    def _add_header_fields(self, pdf: FPDF, data: Dict[str, Any]) -> None:
        left_x, right_x = 10, 110
        line_height = 7
        y = pdf.get_y()
        right_side_y = y

        pdf.set_font("Arial", '', 10)
        m_s_text = str(data.get("M/s", ""))
        m_s_width = 60
        m_s_lines = pdf.multi_cell(m_s_width, line_height, m_s_text, border=0, split_only=True)
        m_s_height = max(line_height, len(m_s_lines) * line_height)

        pdf.set_xy(left_x, y)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(30, m_s_height, "M/s:", border=1, align='L')
        pdf.set_font("Arial", '', 10)
        pdf.multi_cell(60, line_height, m_s_text, border=1, align='L')

        campaign_text = str(data.get("Campaign", ""))
        campaign_lines = pdf.multi_cell(m_s_width, line_height, campaign_text, border=0, split_only=True)
        campaign_height = max(line_height, len(campaign_lines) * line_height)

        pdf.set_xy(left_x, y + m_s_height)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(30, campaign_height, "Campaign:", border=1, align='L')
        pdf.set_font("Arial", '', 10)
        pdf.multi_cell(60, line_height, campaign_text, border=1, align='L')

        left_side_height = m_s_height + campaign_height

        def write_underlined_field(label, value):
            pdf.set_font("Arial", 'B', 10)
            label_str = f"{label}:"
            label_width = pdf.get_string_width(label_str) + 1
            pdf.set_font("Arial", '', 10)
            value_str = str(value)
            value_width = pdf.get_string_width(value_str) + 1
            total_width = label_width + value_width
            start_x = pdf.get_x()
            start_y = pdf.get_y()
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(label_width, line_height, label_str, 0, 0, 'L')
            pdf.set_font("Arial", '', 10)
            pdf.cell(value_width, line_height, value_str, 0, 1, 'L')
            pdf.line(start_x, start_y + line_height, start_x + total_width, start_y + line_height)

        right_x = pdf.w - 60

        pdf.set_xy(right_x, right_side_y)
        write_underlined_field("Date", data.get("Date", ""))
        pdf.set_x(right_x)
        write_underlined_field("Invoice No", data.get("Invoice No", ""))
        pdf.set_x(right_x)
        write_underlined_field("Invoice Month", data.get("Invoice Month", ""))

        right_side_height = line_height * 3
        new_y = max(y + left_side_height, right_side_y + right_side_height)
        pdf.set_y(new_y)
        pdf.ln(5)

    def _add_line_items(self, pdf: FPDF, items: List[Dict[str, str]]) -> None:
        headers = ["Sr.", "Description", "Size", "Duration", "Amount"]
        col_widths = [10, 90, 20, 25, 35]
        start_x = 10
        row_min_height = 15
        top_padding = 2

        pdf.ln(5)
        pdf.set_font("Arial", 'B', 9)
        pdf.set_fill_color(240, 240, 240)
        pdf.set_x(start_x)
        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 8, header, 1, 0, align='C', fill=True)
        pdf.ln()

        pdf.set_font("Arial", '', 11)
        for idx, item in enumerate(items, 1):
            description = item.get("Description", "").strip()
            start = item.get("Campaign Start Date", "").strip()
            end = item.get("Campaign End Date", "").strip()
            full_desc = description
            if start or end:
                full_desc += "\n\n"
            if start:
                full_desc += f"Campaign Start: {start}"
            if end:
                full_desc += f"\nCampaign End: {end}"
            y_start = pdf.get_y()
            max_y = y_start

            pdf.set_xy(start_x, y_start + top_padding)
            pdf.multi_cell(col_widths[0], 5, str(idx), border=0, align='C')
            max_y = max(max_y, pdf.get_y())

            pdf.set_xy(start_x + col_widths[0], y_start + top_padding)
            pdf.multi_cell(col_widths[1], 5, full_desc, border=0, align='L')
            max_y = max(max_y, pdf.get_y())

            pdf.set_xy(start_x + col_widths[0] + col_widths[1], y_start + top_padding)
            pdf.multi_cell(col_widths[2], 5, item.get("Size", ""), border=0, align='C')
            max_y = max(max_y, pdf.get_y())

            pdf.set_xy(start_x + col_widths[0] + col_widths[1] + col_widths[2], y_start + top_padding)
            pdf.multi_cell(col_widths[3], 5, item.get("Duration", ""), border=0, align='C')
            max_y = max(max_y, pdf.get_y())

            amount_val = f"Rs. {item.get('Amount', '')}/-"
            pdf.set_font("Arial", 'B', 11)
            pdf.set_xy(start_x + sum(col_widths[:-1]), y_start + top_padding)
            pdf.multi_cell(col_widths[4], 5, amount_val, border=0, align='C')
            pdf.set_font("Arial", '', 11)
            max_y = max(max_y, pdf.get_y())

            final_y = max(max_y, y_start + row_min_height)
            current_x = start_x
            for w in col_widths:
                pdf.line(current_x, y_start, current_x, final_y)
                current_x += w
            pdf.line(current_x, y_start, current_x, final_y)
            pdf.set_y(final_y)

        remaining_rows = max(0, 6 - len(items))
        for _ in range(remaining_rows):
            y_start = pdf.get_y()
            y_end = y_start + row_min_height
            current_x = start_x
            for w in col_widths:
                pdf.line(current_x, y_start, current_x, y_end)
                current_x += w
            pdf.line(current_x, y_start, current_x, y_end)
            pdf.set_y(y_end)

        table_bottom_y = pdf.get_y()
        pdf.line(start_x, table_bottom_y, start_x + sum(col_widths), table_bottom_y)
        pdf.ln(3)

    def _add_totals_and_footer(self, pdf: FPDF, items: List[Dict[str, str]]) -> None:
        total = 0
        for item in items:
            try:
                amt = float(item.get("Amount", "0").replace(",", ""))
                total += amt
            except:
                continue

        try:
            total_str = locale.currency(total, grouping=True, symbol=False)
        except:
            total_str = f"{total:,.2f}"

        pdf.set_font("Arial", 'B', 10)
        pdf.set_fill_color(245, 245, 245)
        pdf.set_draw_color(0, 0, 0)

        table_x = 10
        table_width = sum([10, 90, 20, 25, 35])
        label_width = table_width - 35
        amount_width = 35

        pdf.set_x(table_x)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(label_width, 10, "TOTAL:", border=1, align='C', fill=True)
        pdf.cell(amount_width, 10, f"PKR {total_str}", border=1, align='R', fill=True)

        pdf.ln(15)

        pdf.set_font("Arial", 'IU', 12)
        try:
            amount_words = num2words(int(round(total)), lang='en_IN').capitalize()
            words = f"Amount in words: {amount_words} rupees only"
        except:
            words = f"Amount in words: {total} rupees only"
        pdf.set_x(10)
        pdf.multi_cell(0, 6, words, 0, 'L')


def get_template_class():
    return InvoiceTemplate()
