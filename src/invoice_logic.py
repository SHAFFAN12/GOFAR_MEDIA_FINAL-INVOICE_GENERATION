import json
from pathlib import Path
from utils import resource_path

class InvoiceNumberGenerator:
    """
    Manages invoice number generation with a persistent counter.
    Uses a 'peek' and 'commit' system to prevent skipping numbers on error.
    """
    def __init__(self, counter_file='invoice_counter.json', config_file='config.json'):
        self.counter_file = Path(resource_path(counter_file))
        if Path(config_file).is_absolute():
            self.config_file = Path(config_file)
        else:
            self.config_file = Path(resource_path(config_file))
        self.counters = self._load_counters()
        self.config = self._load_config()

    def _load_counters(self):
        """Loads the counter file from disk. Returns empty dict if not found."""
        if self.counter_file.exists():
            try:
                with open(self.counter_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def _load_config(self):
        """Loads the main config file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                raise ValueError("Error reading config.json")
        raise FileNotFoundError("config.json not found")

    def _save_counters(self):
        """Saves the current counters to the file."""
        with open(self.counter_file, 'w') as f:
            json.dump(self.counters, f, indent=4)

    def _get_company_key(self, company_name: str) -> str:
        """Generates a consistent key from the company name."""
        return company_name.lower().replace(' ', '_')

    def peek_next(self, company_name: str) -> str:
        """
        Determines the next invoice number without incrementing the counter.
        """
        company_key = self._get_company_key(company_name)
        last_number = self.counters.get(company_key, 0)
        next_number = last_number + 1

        try:
            pattern = self.config["companies"][company_name]["invoice_pattern"]
            return pattern.format(next_number)
        except KeyError:
            # Fallback for any other company not in config
            return f"INV-{next_number}"

    def commit(self, company_name: str):
        """
        Increments and saves the counter for the given company.
        This should only be called after the document is successfully saved.
        """
        company_key = self._get_company_key(company_name)
        last_number = self.counters.get(company_key, 0)
        self.counters[company_key] = last_number + 1
        self._save_counters()

    def set_counter(self, company_name: str, new_next_number: int):
        """
        Sets the counter for a company to a specific value.
        The value provided should be the desired *next* invoice number.
        """
        if not isinstance(new_next_number, int) or new_next_number < 1:
            raise ValueError("Invoice number must be a positive integer.")
            
        company_key = self._get_company_key(company_name)
        # We store the 'last used' number, so subtract 1 from the desired 'next' number.
        self.counters[company_key] = new_next_number - 1
        self._save_counters()
        # Reload counters from disk to ensure consistency
        self.counters = self._load_counters()
