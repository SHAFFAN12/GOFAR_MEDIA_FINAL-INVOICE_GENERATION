from fpdf import FPDF
from .base_template import BaseTemplate
from typing import Dict, Any, List
from num2words import num2words
from datetime import datetime
import locale


class SalesTaxTemplate(BaseTemplate):
    @property
    def template_type(self) -> str:
        return "Sales Tax Invoice"

    def get_template(self) -> Dict[str, Any]:
        return {
            "type": self.template_type,
            "header_fields": [
                ("Custom Title (Optional)", "text"),
                ("M/s", "text"),
                ("Campaign", "text"),
                ("PO Number", "text"), 
                ("NTN", "text"), 
                ("STRN", "text"), 
                ("Company NTN", "text"), 
                ("Company STN", "text"), 
                ("Date", "date"),
                ("Invoice No", "text"),
                ("Invoice Month", "text"),
                ("GST Percentage", "number") # Added GST Percentage field
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

    def validate_data(self, data: Dict[str, Any]) -> bool:
        required = ["M/s", "Campaign", "Date", "Invoice No", "line_items", "Invoice Month"]
        for field in required:
            if field not in data or not data[field]:
                return False
        if "line_items" not in data or not isinstance(data["line_items"], list):
            return False
        for item in data["line_items"]:
            if not all(k in item for k in self.get_template()["line_items"]["columns"]):
                return False
        return True

    def generate_pdf_content(self, pdf: FPDF, data: Dict[str, Any]) -> None:
        pdf.set_font("Arial", 'B', 16)
        title = (data.get("Custom Title (Optional)") or self.template_type).upper()
        pdf.cell(0, 10, title, 0, 1, 'C')
        pdf.set_draw_color(0, 0, 0)
        pdf.set_line_width(0.4)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)

        self._add_header_fields(pdf, data)
        grand_total = self._add_line_items(pdf, data)
        self._add_totals_and_footer(pdf, grand_total)

    def _add_header_fields(self, pdf: FPDF, data: Dict[str, Any]) -> None:
        left_x, right_x = 10, 145
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
        
        # New fields added here
        po_number_text = str(data.get("PO Number", ""))
        po_number_lines = pdf.multi_cell(m_s_width, line_height, po_number_text, border=0, split_only=True)
        po_number_height = max(line_height, len(po_number_lines) * line_height)

        pdf.set_xy(left_x, y + m_s_height + campaign_height)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(30, po_number_height, "PO Number:", border=1, align='L')
        pdf.set_font("Arial", '', 10)
        pdf.multi_cell(60, line_height, po_number_text, border=1, align='L')

        ntn_text = str(data.get("NTN", ""))
        ntn_lines = pdf.multi_cell(m_s_width, line_height, ntn_text, border=0, split_only=True)
        ntn_height = max(line_height, len(ntn_lines) * line_height)

        pdf.set_xy(left_x, y + m_s_height + campaign_height + po_number_height)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(30, ntn_height, "NTN:", border=1, align='L')
        pdf.set_font("Arial", '', 10)
        pdf.multi_cell(60, line_height, ntn_text, border=1, align='L')

        strn_text = str(data.get("STRN", ""))
        strn_lines = pdf.multi_cell(m_s_width, line_height, strn_text, border=0, split_only=True)
        strn_height = max(line_height, len(strn_lines) * line_height)

        pdf.set_xy(left_x, y + m_s_height + campaign_height + po_number_height + ntn_height)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(30, strn_height, "STRN:", border=1, align='L')
        pdf.set_font("Arial", '', 10)
        pdf.multi_cell(60, line_height, strn_text, border=1, align='L')


        left_side_height = m_s_height + campaign_height + po_number_height + ntn_height + strn_height


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

        pdf.set_xy(right_x, right_side_y)
        write_underlined_field("Date", data.get("Date", ""))
        pdf.set_x(right_x)
        write_underlined_field("Invoice Month", data.get("Invoice Month", ""))
        pdf.set_x(right_x)
        write_underlined_field("Invoice No", data.get("Invoice No", ""))
        pdf.set_x(right_x)
        write_underlined_field("Company NTN", data.get("Company NTN", ""))
        pdf.set_x(right_x)
        write_underlined_field("Company STN", data.get("Company STN", ""))

        right_side_height = line_height * 3
        new_y = max(y + left_side_height, right_side_y + right_side_height)
        pdf.set_y(new_y)
        pdf.ln(5)

    def _add_line_items(self, pdf: FPDF, data: Dict[str, Any]) -> float:
        items = data["line_items"]
        headers = ["Sr.", "Description", "Size", "Duration", "Amount"]
        col_widths = [10, 90, 20, 25, 35]
        start_x = 10
        row_min_height = 15
        top_padding = 2
        subtotal = 0.0

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
            
            try:
                subtotal += float(item.get("Amount", "0").replace(",", ""))
            except (ValueError, TypeError):
                pass
            
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
            pdf.set_xy(start_x + col_widths[0] + col_widths[1] + col_widths[2] + col_widths[3], y_start + top_padding)
            pdf.multi_cell(col_widths[4], 5, amount_val, border=0, align='C')
            max_y = max(max_y, pdf.get_y())

            pdf.set_font("Arial", '', 11)
            final_y = max(max_y, y_start + row_min_height)
            current_x = start_x
            for w in col_widths:
                pdf.line(current_x, y_start, current_x, final_y)
                current_x += w
            pdf.line(current_x, y_start, current_x, final_y)
            pdf.set_y(final_y)
        
        # Add GST Row
        padding_top = 8   # upar ka space row ke andar
        gst_rate = float(data.get("GST Percentage", 15))
        gst_total = round(subtotal * gst_rate / 100, 2)
        grand_total = subtotal + gst_total

        
        y_start = pdf.get_y()
        pdf.set_y(y_start + padding_top)

        pdf.set_x(start_x)
        pdf.set_font("Arial", '', 11)
        pdf.cell(col_widths[0], row_min_height, "", border=0, align='C')
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(col_widths[1], row_min_height, f"GST  {gst_rate:.0f}%", border=0, align='L')
        pdf.set_font("Arial", '', 11)
        pdf.cell(sum(col_widths[2:4]), row_min_height, "", border=0, align='C')
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(col_widths[4], row_min_height, f"Rs. {gst_total:,.2f}/=", border=0, align='C')
        pdf.ln()
        
        # Draw lines for the new row
        y_end_gst = pdf.get_y()
        current_x = start_x
        for w in col_widths:
            pdf.line(current_x, y_start, current_x, y_end_gst)
            current_x += w
        pdf.line(current_x, y_start, current_x, y_end_gst)
        
        remaining_rows = max(0, 6 - len(items) - 1) # Adjust for the new row
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
        
        return grand_total

    def _add_totals_and_footer(self, pdf: FPDF, grand_total: float) -> None:
        table_x = 10
        widths = [10, 90, 20, 25, 35] 
        label_width = sum(widths[:-1]) 
        amount_width = widths[-1]
        
        pdf.set_x(table_x)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(label_width, 10, "TOTAL", border=1, align='C', fill=True)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(amount_width, 10, f"Rs. {grand_total:,.2f}/-", border=1, align='R', fill=True)
        pdf.ln(15)
        
        # Amount in Words
        pdf.set_font("Arial", 'IU', 12)
        try:
            amount_words = num2words(int(round(grand_total)), lang='en_IN').capitalize()
            words = f"Amount in words: {amount_words} rupees only"
        except (ValueError, TypeError):
            words = f"Amount in words: {grand_total} rupees only"
        pdf.set_x(10)
        pdf.multi_cell(0, 6, words, 0, 'L')
        

def get_template_class():
    return SalesTaxTemplate()