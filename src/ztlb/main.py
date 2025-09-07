"""FastAPI application for ZTL Maps API."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .database import get_zone_by_id, get_zones_by_city
from .models import CitiesResponse, City, HealthResponse, ZonesResponse, ZTLZone
from .version import __version__

# Create FastAPI app
app = FastAPI(
    title='ZTL Maps API',
    description='API for Italian ZTL (Zona a Traffico Limitato) zones',
    version=__version__,
)

# Add CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],  # Configure properly for production
    allow_credentials=True,
    allow_methods=['GET'],
    allow_headers=['*'],
)


@app.get('/', include_in_schema=False)
async def root() -> dict[str, str]:
    """Root endpoint redirect."""
    return {'message': 'ZTL Maps API', 'docs': '/docs'}


@app.get('/health', response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(status='healthy', version=__version__)


@app.get('/cities', response_model=CitiesResponse)
async def get_cities() -> CitiesResponse:
    """Get list of available cities."""
    # MVP: Only Milano supported
    cities = [City(name='Milano', slug='milano', zone_count=4)]
    return CitiesResponse(cities=cities, total_count=len(cities))


@app.get('/zones/{city}', response_model=ZonesResponse)
async def get_zones(city: str) -> ZonesResponse:
    """Get ZTL zones for a specific city."""
    try:
        zones_data = get_zones_by_city(city.lower())

        if not zones_data:
            raise HTTPException(status_code=404, detail=f'No zones found for city: {city}')

        zones = [ZTLZone(**zone_data) for zone_data in zones_data]

        return ZonesResponse(city=city.title(), zones=zones, total_count=len(zones))

    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail='Zone data not available') from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Error loading zones: {str(e)}') from e


@app.get('/zones/{city}/{zone_id}', response_model=ZTLZone)
async def get_zone(city: str, zone_id: str) -> ZTLZone:
    """Get a specific ZTL zone by ID."""
    try:
        zone_data = get_zone_by_id(zone_id)

        if not zone_data:
            raise HTTPException(status_code=404, detail=f'Zone {zone_id} not found in {city}')

        # Add ID to zone data if not present
        if 'id' not in zone_data:
            zone_data['id'] = zone_id

        return ZTLZone(**zone_data)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Error loading zone: {str(e)}') from e


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=8000)
