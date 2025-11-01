from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseTemplate(ABC):
    """Abstract base class for all document templates."""
    
    @property
    @abstractmethod
    def template_type(self) -> str:
        """Return the type of document this template represents."""
        pass
    
    @abstractmethod
    def get_template(self) -> Dict[str, Any]:
        """Return the template configuration dictionary."""
        pass
    
    @abstractmethod
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate the input data for this template."""
        pass
    
    @abstractmethod
    def generate_pdf_content(self, pdf_generator: 'PDFGenerator', data: Dict[str, Any]) -> None:
        """Generate the PDF content for this template."""
        pass