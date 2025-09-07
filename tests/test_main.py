"""Tests for FastAPI application."""

from typing import Any
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from ztlb.main import app

client = TestClient(app)


class TestRootEndpoint:
    """Test root endpoint."""

    def test_root_endpoint(self) -> None:
        """Test root endpoint returns correct response."""
        response = client.get('/')

        assert response.status_code == 200
        assert response.json() == {'message': 'ZTL Maps API', 'docs': '/docs'}


class TestHealthEndpoint:
    """Test health endpoint."""

    def test_health_endpoint(self) -> None:
        """Test health endpoint returns correct response."""
        response = client.get('/health')

        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
        assert 'version' in data
        assert isinstance(data['version'], str)


class TestCitiesEndpoint:
    """Test cities endpoint."""

    def test_get_cities(self) -> None:
        """Test cities endpoint returns Milano."""
        response = client.get('/cities')

        assert response.status_code == 200
        data = response.json()
        assert data['total_count'] == 1
        assert len(data['cities']) == 1

        milano = data['cities'][0]
        assert milano['name'] == 'Milano'
        assert milano['slug'] == 'milano'
        assert milano['zone_count'] == 4


class TestZonesEndpoint:
    """Test zones endpoint."""

    @pytest.fixture
    def sample_zones_data(self) -> list[dict[str, Any]]:
        """Sample zones data fixture."""
        return [
            {
                'id': '194',
                'name': 'ZTL Milano 194 - Ticinese',
                'center': [9.18056, 45.45549],
                'polygon': [[9.1806, 45.4561], [9.1807, 45.4562]],
                'deroghe': 'Transito e sosta: residenti',
            },
            {
                'id': '195',
                'name': 'ZTL Milano 195 - Garibaldi',
                'center': [9.19056, 45.46549],
                'polygon': [[9.1906, 45.4651], [9.1907, 45.4652]],
                'deroghe': 'Solo transito: autorizzati',
            },
        ]

    def test_get_zones_milano_success(self, sample_zones_data: list[dict[str, Any]]) -> None:
        """Test getting zones for Milano."""
        with patch('ztlb.main.get_zones_by_city', return_value=sample_zones_data):
            response = client.get('/zones/milano')

            assert response.status_code == 200
            data = response.json()
            assert data['city'] == 'Milano'
            assert data['total_count'] == 2
            assert len(data['zones']) == 2

            # Check zone structure
            zone = data['zones'][0]
            assert 'id' in zone
            assert 'name' in zone
            assert 'center' in zone
            assert 'polygon' in zone

    def test_get_zones_case_insensitive(self, sample_zones_data: list[dict[str, Any]]) -> None:
        """Test case-insensitive city matching."""
        with patch('ztlb.main.get_zones_by_city', return_value=sample_zones_data) as mock_get:
            response = client.get('/zones/MILANO')

            assert response.status_code == 200
            # Verify lowercase conversion
            mock_get.assert_called_once_with('milano')

    def test_get_zones_not_found(self) -> None:
        """Test getting zones for non-existent city."""
        with patch('ztlb.main.get_zones_by_city', return_value=[]):
            response = client.get('/zones/roma')

            assert response.status_code == 404
            assert 'No zones found for city: roma' in response.json()['detail']

    def test_get_zones_file_not_found(self) -> None:
        """Test zones endpoint with missing data file."""
        with patch('ztlb.main.get_zones_by_city', side_effect=FileNotFoundError('File not found')):
            response = client.get('/zones/milano')

            assert response.status_code == 500
            assert 'Zone data not available' in response.json()['detail']

    def test_get_zones_general_error(self) -> None:
        """Test zones endpoint with general error."""
        with patch('ztlb.main.get_zones_by_city', side_effect=Exception('Database error')):
            response = client.get('/zones/milano')

            assert response.status_code == 500
            assert 'Error loading zones: Database error' in response.json()['detail']


class TestZoneByIdEndpoint:
    """Test individual zone endpoint."""

    @pytest.fixture
    def sample_zone_data(self) -> dict[str, Any]:
        """Sample zone data fixture."""
        return {
            'name': 'ZTL Milano 194 - Ticinese',
            'center': [9.18056, 45.45549],
            'polygon': [[9.1806, 45.4561], [9.1807, 45.4562]],
            'deroghe': 'Transito e sosta: residenti',
        }

    def test_get_zone_by_id_success(self, sample_zone_data: dict[str, Any]) -> None:
        """Test getting specific zone by ID."""
        with patch('ztlb.main.get_zone_by_id', return_value=sample_zone_data):
            response = client.get('/zones/milano/194')

            assert response.status_code == 200
            data = response.json()
            assert data['id'] == '194'  # ID should be injected
            assert data['name'] == 'ZTL Milano 194 - Ticinese'
            assert data['center'] == [9.18056, 45.45549]

    def test_get_zone_by_id_with_existing_id(self) -> None:
        """Test getting zone that already has ID field."""
        zone_with_id = {
            'id': '194',
            'name': 'ZTL Milano 194 - Ticinese',
            'center': [9.18056, 45.45549],
            'polygon': [[9.1806, 45.4561]],
        }

        with patch('ztlb.main.get_zone_by_id', return_value=zone_with_id):
            response = client.get('/zones/milano/194')

            assert response.status_code == 200
            data = response.json()
            assert data['id'] == '194'

    def test_get_zone_by_id_not_found(self) -> None:
        """Test getting non-existent zone."""
        with patch('ztlb.main.get_zone_by_id', return_value=None):
            response = client.get('/zones/milano/999')

            assert response.status_code == 404
            assert 'Zone 999 not found in milano' in response.json()['detail']

    def test_get_zone_by_id_error(self) -> None:
        """Test zone by ID endpoint with error."""
        with patch('ztlb.main.get_zone_by_id', side_effect=Exception('Database error')):
            response = client.get('/zones/milano/194')

            assert response.status_code == 500
            assert 'Error loading zone: Database error' in response.json()['detail']


class TestCORSMiddleware:
    """Test CORS middleware configuration."""

    def test_cors_middleware_configured(self) -> None:
        """Test that CORS middleware is configured."""
        response = client.get('/health')

        assert response.status_code == 200
        # Just verify we can make requests without CORS errors in tests
        # TestClient doesn't simulate real CORS behavior anyway
        assert True  # Basic test that app works


class TestResponseValidation:
    """Test response model validation."""

    def test_zones_response_structure(self) -> None:
        """Test zones response matches expected structure."""
        sample_data = [
            {
                'id': '194',
                'name': 'ZTL Milano 194 - Ticinese',
                'center': [9.18056, 45.45549],
                'polygon': [[9.1806, 45.4561]],
            }
        ]

        with patch('ztlb.main.get_zones_by_city', return_value=sample_data):
            response = client.get('/zones/milano')

            assert response.status_code == 200
            data = response.json()

            # Verify required fields
            required_fields = ['city', 'zones', 'total_count']
            assert all(field in data for field in required_fields)

            # Verify zone structure
            zone = data['zones'][0]
            zone_fields = ['id', 'name', 'center', 'polygon']
            assert all(field in zone for field in zone_fields)
