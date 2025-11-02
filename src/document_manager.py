import os
import importlib
import sys
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from pdf_generator import PDFGenerator
from utils import get_output_dir, resource_path
from invoice_logic import InvoiceNumberGenerator

def _sanitize_filename(name: str) -> str:
    """Sanitizes a string to be safe for use in a filename."""
    s = str(name).strip().replace(' ', '_')
    s = re.sub(r'[\\/:*?"<>|]', '', s) # Remove invalid characters
    return s


class DocumentManager:
    """Manages document templates and generation process."""
    
    def __init__(self, config_file='config.json'):
        """Initialize with loaded templates."""
        try:
            # First try using resource_path
            self.config_file = Path(resource_path(config_file))
            if not self.config_file.exists() and hasattr(sys, '_MEIPASS'):
                # If we're in a PyInstaller bundle and resource_path failed, try executable directory
                self.config_file = Path(sys.executable).parent / config_file
        except Exception:
            # If all else fails, try current directory
            self.config_file = Path(config_file)
            
        self.config = self._load_config()
        self.templates = self._load_templates()
        self.signature_path: Optional[str] = None
        self.stamp_path: Optional[str] = None
        self.invoice_generator = InvoiceNumberGenerator(config_file=self.config_file)

    def _load_config(self):
        """Loads the main config file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                raise ValueError("Error reading config.json")
        raise FileNotFoundError("config.json not found")

    def _load_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load all templates from the templates directory."""
        templates = {}
        templates_dir = Path(resource_path("src/templates"))

        # Ensure current directory is in Python path
        if str(Path(__file__).parent) not in sys.path:
            sys.path.insert(0, str(Path(__file__).parent))

        for filename in os.listdir(templates_dir):
            if filename.endswith(".py") and filename not in ("__init__.py", "base_template.py"):
                try:
                    module_name = f"templates.{filename[:-3]}"
                    module = importlib.import_module(module_name)
                    template_class = module.get_template_class()
                    template_data = template_class.get_template()
                    template_data["template_class"] = template_class  # Attach the class instance
                    templates[template_data["type"]] = template_data
                except (ImportError, AttributeError) as e:
                    print(f"Error loading template {filename}: {e}")
        return templates

    def get_letterhead_path(self, company: str) -> Optional[str]:
        """Find the appropriate letterhead image for a company from the config."""
        try:
            letterhead_filename = self.config["companies"][company]["letterhead"]
            letterhead_path = Path(resource_path("assets/letterheads")) / letterhead_filename
            if letterhead_path.exists():
                return str(letterhead_path)
            return None
        except KeyError:
            return None

    def generate_document(
        self,
        company: str,
        doc_type: str,
        data: Optional[Dict[str, Any]] = None,
        is_resave: bool = False
    ) -> str:
        """Generate a complete document with the given parameters."""
        template = self.templates.get(doc_type)
        if not template:
            raise ValueError(f"Unknown document type: {doc_type}")
        
        data = data or {}

        is_invoice = "Invoice" in doc_type
        # Only generate a new invoice number if it's a new document
        if is_invoice and not is_resave:
            invoice_no = self.invoice_generator.peek_next(company)
            data["Invoice No"] = invoice_no

        letterhead = self.get_letterhead_path(company)
        if not letterhead:
            raise FileNotFoundError(
                f"Letterhead not found for {company}. "
                f"Please check that the filename in config.json exists in assets/letterheads/"
            )

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = get_output_dir()
        
        # Incorporate M/s name and company into filename
        ms_name = data.get("M/s", "")
        company_prefix = company.split(' ')[0]  # e.g., "Glory" or "GoFar"

        if ms_name:
            sanitized_ms_name = _sanitize_filename(ms_name)
            filename_base = f"{sanitized_ms_name}_{company_prefix.replace(' ', '_')}_{doc_type.replace(' ', '_')}"
        else:
            filename_base = f"{company_prefix.replace(' ', '_')}_{doc_type.replace(' ', '_')}"
        
        filename = output_dir / f"{filename_base}_{timestamp}.pdf"

        # Create and configure PDF generator
        pdf_gen = PDFGenerator()
        pdf_gen.generate(
            company=company,
            doc_type=doc_type,
            template=template,
            letterhead_path=letterhead,
            output_path=str(filename),
            data=data,
            signature_path=self.signature_path,
            stamp_path=self.stamp_path
        )

        # --- Commit the invoice number only for new invoices ---
        if is_invoice and not is_resave:
            self.invoice_generator.commit(company)

        # Save data to a JSON file for future editing
        data_to_save = {
            "company": company,
            "doc_type": doc_type,
            "form_data": data,
        }
        json_path = filename.with_suffix(".json")
        with open(json_path, "w") as f:
            json.dump(data_to_save, f, indent=4)

        return str(filename.absolute())
