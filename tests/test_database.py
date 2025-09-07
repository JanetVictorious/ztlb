"""Tests for database operations."""

import json
from typing import Any
from unittest.mock import mock_open, patch

import pytest

from ztlb.database import get_all_zones, get_zone_by_id, get_zones_by_city, load_zones


class TestLoadZones:
    """Test load_zones function."""

    @pytest.fixture
    def sample_zones_json(self) -> dict[str, Any]:
        """Sample zones data fixture."""
        return {
            '194': {
                'name': 'ZTL Milano 194 - Ticinese',
                'center': [9.18056, 45.45549],
                'polygon': [[9.1806, 45.4561], [9.1807, 45.4562]],
                'deroghe': 'Transito e sosta: residenti',
            },
            '195': {
                'name': 'ZTL Milano 195 - Garibaldi',
                'center': [9.19056, 45.46549],
                'polygon': [[9.1906, 45.4651], [9.1907, 45.4652]],
                'deroghe': 'Solo transito: autorizzati',
            },
        }

    def test_load_zones_success(self, sample_zones_json: dict[str, Any]) -> None:
        """Test successful loading of zones from JSON file."""
        mock_file_content = json.dumps(sample_zones_json)

        with patch('pathlib.Path.open', mock_open(read_data=mock_file_content)):
            zones = load_zones()

            assert len(zones) == 2
            assert '194' in zones
            assert '195' in zones
            assert zones['194']['name'] == 'ZTL Milano 194 - Ticinese'
            assert zones['195']['center'] == [9.19056, 45.46549]

    def test_load_zones_file_not_found(self) -> None:
        """Test handling of missing zones file."""
        with (
            patch('pathlib.Path.open', side_effect=FileNotFoundError('File not found')),
            pytest.raises(FileNotFoundError),
        ):
            load_zones()

    def test_load_zones_invalid_json(self) -> None:
        """Test handling of malformed JSON file."""
        mock_file_content = '{"invalid": json content'

        with (
            patch('pathlib.Path.open', mock_open(read_data=mock_file_content)),
            pytest.raises(json.JSONDecodeError),
        ):
            load_zones()

    def test_load_zones_empty_file(self) -> None:
        """Test handling of empty JSON file."""
        mock_file_content = '{}'

        with patch('pathlib.Path.open', mock_open(read_data=mock_file_content)):
            zones = load_zones()

            assert zones == {}


class TestGetZoneById:
    """Test get_zone_by_id function."""

    @pytest.fixture
    def mock_zones_data(self) -> dict[str, Any]:
        """Mock zones data fixture."""
        return {
            '194': {
                'name': 'ZTL Milano 194 - Ticinese',
                'center': [9.18056, 45.45549],
                'polygon': [[9.1806, 45.4561]],
            },
            '195': {
                'name': 'ZTL Milano 195 - Garibaldi',
                'center': [9.19056, 45.46549],
                'polygon': [[9.1906, 45.4651]],
            },
        }

    def test_get_zone_by_id_found(self, mock_zones_data: dict[str, Any]) -> None:
        """Test getting existing zone by ID."""
        with patch('ztlb.database.load_zones', return_value=mock_zones_data):
            zone = get_zone_by_id('194')

            assert zone is not None
            assert zone['name'] == 'ZTL Milano 194 - Ticinese'
            assert zone['center'] == [9.18056, 45.45549]

    def test_get_zone_by_id_not_found(self, mock_zones_data: dict[str, Any]) -> None:
        """Test getting non-existent zone by ID."""
        with patch('ztlb.database.load_zones', return_value=mock_zones_data):
            zone = get_zone_by_id('999')

            assert zone is None

    def test_get_zone_by_id_empty_data(self) -> None:
        """Test getting zone from empty data."""
        with patch('ztlb.database.load_zones', return_value={}):
            zone = get_zone_by_id('194')

            assert zone is None


class TestGetAllZones:
    """Test get_all_zones function."""

    @pytest.fixture
    def mock_zones_data(self) -> dict[str, Any]:
        """Mock zones data fixture."""
        return {
            '194': {
                'name': 'ZTL Milano 194 - Ticinese',
                'center': [9.18056, 45.45549],
                'polygon': [[9.1806, 45.4561]],
            },
            '195': {
                'name': 'ZTL Milano 195 - Garibaldi',
                'center': [9.19056, 45.46549],
                'polygon': [[9.1906, 45.4651]],
            },
        }

    def test_get_all_zones_success(self, mock_zones_data: dict[str, Any]) -> None:
        """Test getting all zones as list with ID added."""
        with patch('ztlb.database.load_zones', return_value=mock_zones_data):
            zones = get_all_zones()

            assert len(zones) == 2
            assert all('id' in zone for zone in zones)

            # Check that IDs are correctly added
            zone_ids = [zone['id'] for zone in zones]
            assert '194' in zone_ids
            assert '195' in zone_ids

            # Check zone data integrity
            zone_194 = next(zone for zone in zones if zone['id'] == '194')
            assert zone_194['name'] == 'ZTL Milano 194 - Ticinese'

    def test_get_all_zones_empty_data(self) -> None:
        """Test getting all zones from empty data."""
        with patch('ztlb.database.load_zones', return_value={}):
            zones = get_all_zones()

            assert zones == []


class TestGetZonesByCity:
    """Test get_zones_by_city function."""

    @pytest.fixture
    def mock_zones_data(self) -> dict[str, Any]:
        """Mock zones data fixture."""
        return {
            '194': {
                'name': 'ZTL Milano 194 - Ticinese',
                'center': [9.18056, 45.45549],
                'polygon': [[9.1806, 45.4561]],
            },
            '195': {
                'name': 'ZTL Milano 195 - Garibaldi',
                'center': [9.19056, 45.46549],
                'polygon': [[9.1906, 45.4651]],
            },
        }

    def test_get_zones_by_city_milano(self, mock_zones_data: dict[str, Any]) -> None:
        """Test getting zones for Milano."""
        with patch('ztlb.database.load_zones', return_value=mock_zones_data):
            zones = get_zones_by_city('milano')

            assert len(zones) == 2
            assert all('id' in zone for zone in zones)

    def test_get_zones_by_city_case_insensitive(self, mock_zones_data: dict[str, Any]) -> None:
        """Test case insensitive city matching."""
        with patch('ztlb.database.load_zones', return_value=mock_zones_data):
            zones_upper = get_zones_by_city('MILANO')
            zones_mixed = get_zones_by_city('Milano')
            zones_lower = get_zones_by_city('milano')

            assert len(zones_upper) == 2
            assert len(zones_mixed) == 2
            assert len(zones_lower) == 2

    def test_get_zones_by_city_unsupported_city(self) -> None:
        """Test getting zones for unsupported city."""
        zones = get_zones_by_city('roma')

        assert zones == []

    def test_get_zones_by_city_default_parameter(self, mock_zones_data: dict[str, Any]) -> None:
        """Test default city parameter (milano)."""
        with patch('ztlb.database.load_zones', return_value=mock_zones_data):
            zones = get_zones_by_city()  # No city specified, should default to milano

            assert len(zones) == 2
