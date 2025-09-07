"""Tests for Pydantic models."""

from typing import Any

import pytest
from pydantic import ValidationError

from ztlb.models import CitiesResponse, City, HealthResponse, ZonesResponse, ZTLZone


class TestZTLZone:
    """Test ZTLZone model."""

    @pytest.fixture
    def valid_zone_data(self) -> dict[str, Any]:
        """Valid zone data fixture."""
        return {
            'id': '194',
            'name': 'ZTL Milano 194 - Ticinese',
            'center': [9.18056, 45.45549],
            'polygon': [[9.1806, 45.4561], [9.1807, 45.4562], [9.1806, 45.4561]],
        }

    @pytest.fixture
    def full_zone_data(self, valid_zone_data: dict[str, Any]) -> dict[str, Any]:
        """Zone data with all optional fields."""
        return {
            **valid_zone_data,
            'deroghe': 'Transito e sosta: residenti',
            'ordinanza': '697/2021',
            'val_inizio': '2021-05-04 00:00:00+02',
            'val_fine': None,
            'tratto': None,
        }

    def test_valid_zone_creation(self, valid_zone_data: dict[str, Any]) -> None:
        """Test creating a valid ZTL zone."""
        zone = ZTLZone(**valid_zone_data)

        assert zone.id == '194'
        assert zone.name == 'ZTL Milano 194 - Ticinese'
        assert zone.center == [9.18056, 45.45549]
        assert len(zone.polygon) == 3
        assert zone.deroghe is None

    def test_full_zone_creation(self, full_zone_data: dict[str, Any]) -> None:
        """Test creating zone with all fields."""
        zone = ZTLZone(**full_zone_data)

        assert zone.deroghe == 'Transito e sosta: residenti'
        assert zone.ordinanza == '697/2021'
        assert zone.val_inizio == '2021-05-04 00:00:00+02'
        assert zone.val_fine is None

    def test_missing_required_fields(self) -> None:
        """Test validation errors for missing required fields."""
        with pytest.raises(ValidationError) as exc_info:
            ZTLZone(name='Test Zone')

        errors = exc_info.value.errors()
        missing_fields = {error['loc'][0] for error in errors}
        expected_fields = {'id', 'center', 'polygon'}

        assert expected_fields.issubset(missing_fields)

    def test_invalid_coordinate_types(self, valid_zone_data: dict[str, Any]) -> None:
        """Test validation for invalid coordinate types."""
        # Invalid center coordinates
        invalid_data = {**valid_zone_data, 'center': ['invalid', 'coords']}
        with pytest.raises(ValidationError):
            ZTLZone(**invalid_data)

        # Invalid polygon coordinates
        invalid_data = {**valid_zone_data, 'polygon': [['invalid', 'coords']]}
        with pytest.raises(ValidationError):
            ZTLZone(**invalid_data)


class TestCity:
    """Test City model."""

    def test_valid_city_creation(self) -> None:
        """Test creating a valid city."""
        city = City(name='Milano', slug='milano', zone_count=4)

        assert city.name == 'Milano'
        assert city.slug == 'milano'
        assert city.zone_count == 4

    def test_missing_required_fields(self) -> None:
        """Test validation errors for missing required fields."""
        with pytest.raises(ValidationError) as exc_info:
            City(name='Milano')

        errors = exc_info.value.errors()
        missing_fields = {error['loc'][0] for error in errors}

        assert 'slug' in missing_fields
        assert 'zone_count' in missing_fields

    def test_invalid_zone_count_type(self) -> None:
        """Test validation for invalid zone_count type."""
        with pytest.raises(ValidationError):
            City(name='Milano', slug='milano', zone_count='invalid')


class TestZonesResponse:
    """Test ZonesResponse model."""

    @pytest.fixture
    def sample_zones(self) -> list[ZTLZone]:
        """Sample zones fixture."""
        return [
            ZTLZone(
                id='194',
                name='ZTL 194',
                center=[9.18, 45.45],
                polygon=[[9.18, 45.45], [9.19, 45.46]],
            ),
            ZTLZone(
                id='195',
                name='ZTL 195',
                center=[9.20, 45.47],
                polygon=[[9.20, 45.47], [9.21, 45.48]],
            ),
        ]

    def test_valid_zones_response(self, sample_zones: list[ZTLZone]) -> None:
        """Test creating a valid zones response."""
        response = ZonesResponse(city='Milano', zones=sample_zones, total_count=2)

        assert response.city == 'Milano'
        assert len(response.zones) == 2
        assert response.total_count == 2
        assert all(isinstance(zone, ZTLZone) for zone in response.zones)

    def test_empty_zones_list(self) -> None:
        """Test zones response with empty zones list."""
        response = ZonesResponse(city='Roma', zones=[], total_count=0)

        assert response.city == 'Roma'
        assert response.zones == []
        assert response.total_count == 0


class TestCitiesResponse:
    """Test CitiesResponse model."""

    @pytest.fixture
    def sample_cities(self) -> list[City]:
        """Sample cities fixture."""
        return [
            City(name='Milano', slug='milano', zone_count=4),
            City(name='Roma', slug='roma', zone_count=0),
        ]

    def test_valid_cities_response(self, sample_cities: list[City]) -> None:
        """Test creating a valid cities response."""
        response = CitiesResponse(cities=sample_cities, total_count=2)

        assert len(response.cities) == 2
        assert response.total_count == 2
        assert all(isinstance(city, City) for city in response.cities)


class TestHealthResponse:
    """Test HealthResponse model."""

    def test_valid_health_response(self) -> None:
        """Test creating a valid health response."""
        response = HealthResponse(status='healthy', version='1.0.0')

        assert response.status == 'healthy'
        assert response.version == '1.0.0'

    def test_missing_required_fields(self) -> None:
        """Test validation errors for missing required fields."""
        with pytest.raises(ValidationError) as exc_info:
            HealthResponse(status='healthy')

        errors = exc_info.value.errors()
        missing_fields = {error['loc'][0] for error in errors}

        assert 'version' in missing_fields
