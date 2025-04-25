import typing as t
from dataclasses import dataclass

from src.util.dataclass import to_instance
from src.util.http import APIHTTPClient


@dataclass
class Location:
    latitude: float
    longitude: float
    name: str
    country: str | None = None
    state: str | None = None

    @property
    def display_name(self) -> str:
        if self.state:
            return f"{self.name} - {self.state}"
        return self.name

    @property
    def complete_name(self) -> str:
        if self.country:
            return f"{self.display_name} ({self.country})"
        return self.display_name


@dataclass
class Forecast:
    latitude: float
    longitude: float
    current_units: dict[str, str]
    current: dict[str, t.Any]
    hourly_units: dict[str, str]
    hourly: dict[str, list[t.Any]]
    daily_units: dict[str, str]
    daily: dict[str, list[t.Any]]

    @property
    def current_with_units(self) -> dict[str, str]:
        return {key: f"{self.current[key]}{self.current_units[key]}" for key in self.current.keys()}

    @property
    def hourly_with_units(self) -> dict[str, list[t.Any]]:
        return {key: [f"{x}{self.hourly_units[key]}" for x in self.hourly[key]] for key in self.hourly.keys()}

    @property
    def daily_with_units(self) -> dict[str, list[t.Any]]:
        return {key: [f"{x}{self.daily_units[key]}" for x in self.daily[key]] for key in self.daily.keys()}


class OpenMeteo(APIHTTPClient):
    async def search_location(
        self,
        name: str,
        /,
        *,
        limit: int = 25,
        language: str = "pt",
    ) -> list[Location]:
        # Docs: https://open-meteo.com/en/docs/geocoding-api
        data = await self.request(
            "GET",
            "https://geocoding-api.open-meteo.com/v1/search",
            params={
                "name": name,
                "count": limit,
                "language": language,
                "format": "json",
            },
        )
        return [to_instance(result, Location) for result in data.get("results", [])]  # type: ignore

    async def fetch_forecast(
        self,
        latitude: float,
        longitude: float,
        /,
        *,
        model: str = "best_match",
        forecast_days: int = 1,
        timezone: str = "America/Sao_Paulo",
        current: str = "temperature_2m,apparent_temperature",
        hourly: str = "temperature_2m,apparent_temperature",
        daily: str = "temperature_2m_max,temperature_2m_min,apparent_temperature_max,apparent_temperature_min",
    ) -> Forecast:
        # Docs: https://open-meteo.com/en/docs
        data = await self.request(
            "GET",
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "models": model,
                "forecast_days": str(forecast_days),
                "timezone": timezone,
                "current": current,
                "hourly": hourly,
                "daily": daily,
            },
        )
        return to_instance(data, Forecast)  # type: ignore[arg-type]
