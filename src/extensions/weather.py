import disnake
from disnake.ext import commands
from disnake.ext.commands.errors import BadArgument, MissingRequiredArgument
from disnake_plugins import Plugin

from src import config
from src.api.open_meteo import Location, OpenMeteo
from src.bot import Bot as _Bot
from src.util.persistent_dict import PersistentDict


class Bot(_Bot):
    open_meteo: OpenMeteo
    weather_data: PersistentDict


plugin = Plugin[Bot]()


@plugin.load_hook()
async def weather_load_hook() -> None:
    plugin.bot.open_meteo = OpenMeteo()
    plugin.bot.weather_data = PersistentDict.from_file(config.File.weather)


@plugin.unload_hook()
async def weather_unload_hook() -> None:
    await plugin.bot.open_meteo.close()


async def _weather_command(
    inter: commands.Context[Bot] | disnake.ApplicationCommandInteraction, *, city: str
) -> None:
    # TODO: improve this code (split)
    locations = await plugin.bot.open_meteo.search_location(city.split(" - ")[0])
    if not locations:
        raise BadArgument(f"No weather data found for {city!r}.")
    # TODO: improve this code (iterator)
    location: Location = next(
        (loc for loc in locations if city.lower() == loc.display_name.lower()),
        next((loc for loc in locations if city.lower() in loc.display_name.lower()), locations[0]),
    )
    forecast = await plugin.bot.open_meteo.fetch_forecast(location.latitude, location.longitude)
    temperature = forecast.current_with_units["temperature_2m"]
    temperature_apparent = forecast.current_with_units["apparent_temperature"]
    temperature_min = forecast.daily_with_units["temperature_2m_min"][0]
    temperature_max = forecast.daily_with_units["temperature_2m_max"][0]
    content = (
        f"{location.display_name}:"
        f" {temperature} (sensação de {temperature_apparent}),"
        f" variando hoje entre {temperature_min} e {temperature_max}"
    )
    plugin.bot.weather_data[inter.author.id] = city
    await plugin.bot.reply(inter, content)


@plugin.command(
    name="weather", aliases=["w", "clima"], description="Retrieve the current weather for a specified city."
)
async def weather_prefix_command(ctx: commands.Context[Bot], *, city: str | None = None) -> None:
    if not city and plugin.bot.weather_data.get(ctx.author.id):
        city = plugin.bot.weather_data[ctx.author.id]
    if not city:
        raise MissingRequiredArgument(city)
    await _weather_command(ctx, city=city)


@plugin.slash_command(name="weather")
async def weather_slash_command(inter: disnake.ApplicationCommandInteraction, city: str) -> None:
    """
    Retrieve the current weather for a specified city.

    Parameters
    ----------
    city: The name of the city.
    """
    await inter.response.defer()
    await _weather_command(inter, city=city)


@weather_slash_command.autocomplete("city")
async def weather_autocomplete(self, inter: disnake.ApplicationCommandInteraction, name: str) -> list[str]:
    if len(name) < 3:
        if plugin.bot.weather_data.get(inter.author.id):
            return [plugin.bot.weather_data[inter.author.id]]
        return []
    locations = await plugin.bot.open_meteo.search_location(name)
    return [location.complete_name for location in locations]


setup, teardown = plugin.create_extension_handlers()
