"""Client for the environment agency flood alert api"""
import logging

import aiohttp

AREA_ENDPOINT = "http://environment.data.gov.uk/flood-monitoring/id/floodAreas?lat=%s&long=%s&dist=%s"
FLOODS_ENDPOINT = (
    "http://environment.data.gov.uk/flood-monitoring/id/floods?lat=%s&long=%s&dist=%s"
)


_LOGGER = logging.getLogger(__name__)


class FloodAlertsClient:
    """Client for the Environment Agency flood warning API"""

    def __init__(self, latitude, longitude, distance):
        """Initialize the client"""
        self.latitude = latitude
        self.longitude = longitude
        self.distance = distance
        self.flood_areas = None

    async def async_get_area_data(self):
        """Request raw data from the endpoint"""
        request_url = AREA_ENDPOINT % (self.latitude, self.longitude, self.distance)
        _LOGGER.debug("Endpoint URL = %s", request_url)
        async with aiohttp.ClientSession() as session:
            async with session.get(request_url) as resp:
                json_response = await resp.json()
                return json_response

    async def async_get_flood_data(self):
        """Request raw data from the endpoint"""
        request_url = FLOODS_ENDPOINT % (self.latitude, self.longitude, self.distance)
        _LOGGER.debug("Endpoint URL = %s", request_url)
        async with aiohttp.ClientSession() as session:
            async with session.get(request_url) as resp:
                json_response = await resp.json()
                return json_response

    def process_area_data(self, raw_data):
        """Process raw data"""

        self.flood_areas = {}
        for raw_data_item in raw_data["items"]:
            data_item = {}
            data_item["description"] = raw_data_item["description"]
            data_item["name"] = raw_data_item["notation"]
            data_item["friendly_name"] = raw_data_item["label"]
            self.flood_areas[data_item["name"]] = data_item

    def process_flood_data(self, raw_data):
        """Process raw data"""

        # reset flood data
        for _, each in self.flood_areas.items():
            each["current_warning"] = []
            each["risk_level"] = 0

        for raw_data_item in raw_data["items"]:
            flood_area = self.flood_areas[raw_data_item["floodAreaID"]]

            current_warning = {}

            current_warning["message"] = raw_data_item["message"]
            current_warning["severity"] = raw_data_item["severity"]
            current_warning["severity_level"] = raw_data_item["severityLevel"]
            current_warning["time_message_changed"] = raw_data_item[
                "timeMessageChanged"
            ]
            current_warning["time_raised"] = raw_data_item["timeRaised"]
            current_warning["time_severity_changed"] = raw_data_item[
                "timeSeverityChanged"
            ]
            current_warning["tidal_alert"] = raw_data_item["isTidal"]

            flood_area["current_warning"].append(current_warning)

            flood_area["risk_level"] = 4 - int(raw_data_item["severityLevel"])

    async def async_get_data(self):
        """Request processed data from the endpoint"""
        if self.flood_areas is None:
            raw_areas = await self.async_get_area_data()
            self.process_area_data(raw_areas)

        raw_floods = await self.async_get_flood_data()
        self.process_flood_data(raw_floods)

        return self.flood_areas
