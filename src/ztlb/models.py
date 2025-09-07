"""Pydantic models for ZTL API responses."""

from datetime import datetime

from pydantic import BaseModel, Field


class ZTLZone(BaseModel):
    """ZTL zone data model."""

    id: str = Field(..., description='Zone identifier')
    name: str = Field(..., description='Zone name')
    center: list[float] = Field(..., description='Zone center coordinates [lng, lat]')
    polygon: list[list[float]] = Field(..., description='Zone boundary polygon coordinates')

    # Regulatory data (optional fields from Milano data)
    deroghe: str | None = Field(None, description='Traffic exceptions and permits')
    ordinanza: str | None = Field(None, description='Municipal ordinance reference')
    val_inizio: str | None = Field(None, description='Validity start date')
    val_fine: str | None = Field(None, description='Validity end date')
    tratto: str | None = Field(None, description='Street section reference')

    class Config:
        """Pydantic config."""

        json_encoders = {datetime: lambda v: v.isoformat()}


class City(BaseModel):
    """City information model."""

    name: str = Field(..., description='City name')
    slug: str = Field(..., description='URL-friendly city identifier')
    zone_count: int = Field(..., description='Number of ZTL zones')


class ZonesResponse(BaseModel):
    """Response model for zones list."""

    city: str = Field(..., description='City name')
    zones: list[ZTLZone] = Field(..., description='List of ZTL zones')
    total_count: int = Field(..., description='Total number of zones')


class CitiesResponse(BaseModel):
    """Response model for cities list."""

    cities: list[City] = Field(..., description='Available cities')
    total_count: int = Field(..., description='Total number of cities')


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description='Service status')
    version: str = Field(..., description='API version')
