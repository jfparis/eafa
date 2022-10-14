"""Platform for sensor integration."""
from __future__ import annotations

from datetime import timedelta
import logging

import async_timeout
import aiohttp

from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .client import FloodAlertsClient
from .const import (
    DOMAIN,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_DISTANCE,
    REFRESH,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Config entry example."""

    latitude = entry.data.get(CONF_LATITUDE)
    longitude = entry.data.get(CONF_LONGITUDE)
    distance = entry.data.get(CONF_DISTANCE)

    coordinator = FloodAlertsCoordinator(hass, latitude, longitude, distance)

    # Fetch initial data so we have data when entities subscribe
    #
    # If the refresh fails, async_config_entry_first_refresh will
    # raise ConfigEntryNotReady and setup will try again later
    #
    # If you do not want to retry setup on failure, use
    # coordinator.async_refresh() instead
    #
    await coordinator.async_config_entry_first_refresh()

    async_add_entities(FloodAlert(coordinator, idx) for idx in coordinator.data)


class FloodAlertsCoordinator(DataUpdateCoordinator):
    """My custom coordinator."""

    def __init__(self, hass, latitude, longitude, distance):
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            # Name of the data. For logging purposes.
            name=DOMAIN,
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(minutes=REFRESH),
        )
        self.my_api = FloodAlertsClient(latitude, longitude, distance)

    async def _async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        try:
            # Note: asyncio.TimeoutError and aiohttp.ClientError are already
            # handled by the data update coordinator.
            async with async_timeout.timeout(10):
                return await self.my_api.async_get_data()
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err


class FloodAlert(CoordinatorEntity):
    """An entity using CoordinatorEntity.

    The CoordinatorEntity class provides:
      should_poll
      async_update
      async_added_to_hass
      available

    """

    def __init__(self, coordinator, idx):
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator)
        self.idx = idx
        # self.entity_id = coordinator[self.idx]["name"]
        # self.friendly_name = f"{self.coordinator.data[self.idx]['friendly_name']}"

    # @property
    # def name(self):
    #    """Return the name of the sensor."""
    #    return f"{self.coordinator.data[self.idx]['friendly_name']}"

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self.coordinator.data[self.idx]

    @property
    def unique_id(self) -> str | None:
        """Return a unique ID."""
        return f"{self.coordinator.data[self.idx]['name']}"

    @property
    def state(self):
        """Return the state of the sensor."""
        _LOGGER.debug("sensor %s updating state", self.idx)
        # _LOGGER.debug(self.coordinator.data[self.idx])
        if self.coordinator.data[self.idx]["risk_level"] > 0:
            return "on"
        else:
            return "off"
