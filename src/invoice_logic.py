import json
from pathlib import Path

class InvoiceNumberGenerator:
    """
    Manages invoice number generation with a persistent counter.
    Uses a 'peek' and 'commit' system to prevent skipping numbers on error.
    """
    def __init__(self, counter_file='invoice_counter.json', config_file='config.json'):
        self.counter_file = Path(__file__).parent.parent / counter_file
        self.config_file = Path(__file__).parent.parent / config_file
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
