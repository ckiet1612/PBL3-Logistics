# services/ward_service.py
"""Service to load and query province-ward data."""

import json
import os

class WardService:
    """Load ward data from JSON and provide query methods."""

    _instance = None
    _data = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_data()
        return cls._instance

    def _load_data(self):
        """Load province-ward mapping from JSON file."""
        json_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'data', 'province_wards.json'
        )

        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                self._data = json.load(f)
        except FileNotFoundError:
            print(f"Warning: {json_path} not found")
            self._data = {}

    def get_provinces(self):
        """Get list of all provinces."""
        return sorted(self._data.keys())

    def get_wards(self, province: str) -> list:
        """Get list of wards for a given province."""
        if not province or province not in self._data:
            return []
        return self._data.get(province, [])

    def has_province(self, province: str) -> bool:
        """Check if province exists in data."""
        return province in self._data
