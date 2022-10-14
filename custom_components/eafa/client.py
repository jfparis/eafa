"""Client for the environment agency flood alert api"""
import aiohttp
import logging

ENDPOINT = "http://environment.data.gov.uk/flood-monitoring/id/floodAreas?lat=%s&long=%s&dist=%s"

_LOGGER = logging.getLogger(__name__)


class FloodAlertsClient:
    """Client for the Environment Agency flood warning API"""

    def __init__(self, latitude, longitude, distance):
        """Initialize the client"""
        self.latitude = latitude
        self.longitude = longitude
        self.distance = distance

    async def async_raw_get_data(self):
        """Request raw data from the endpoint"""
        request_url = ENDPOINT % (self.latitude, self.longitude, self.distance)
        _LOGGER.debug("Endpoint URL = %s", request_url)
        async with aiohttp.ClientSession() as session:
            async with session.get(request_url) as resp:
                json_response = await resp.json()
                return json_response

    def process_data(self, raw_data):
        """Process raw data"""

        areas = {}

        for raw_data_item in raw_data["items"]:
            data_item = {}
            data_item["description"] = raw_data_item["description"]
            data_item["name"] = raw_data_item["notation"]
            data_item["friendly_name"] = raw_data_item["label"]
            data_item["current_warning"] = {}
            if "currentWarning" in raw_data_item.keys():
                data_item["current_warning"]["message"] = raw_data_item[
                    "currentWarning"
                ]["message"]
                data_item["current_warning"]["severity"] = raw_data_item[
                    "currentWarning"
                ]["severity"]
                data_item["current_warning"]["severity_level"] = raw_data_item[
                    "currentWarning"
                ]["severityLevel"]
                data_item["current_warning"]["time_message_changed"] = raw_data_item[
                    "currentWarning"
                ]["timeMessageChanged"]
                data_item["current_warning"]["time_raised"] = raw_data_item[
                    "currentWarning"
                ]["timeRaised"]
                data_item["current_warning"]["time_severity_changed"] = raw_data_item[
                    "currentWarning"
                ]["timeSeverityChanged"]
                data_item["current_warning"]["tidal_alert"] = raw_data_item[
                    "currentWarning"
                ]["isTidal"]
                data_item["risk_level"] = 4 - int(
                    raw_data_item["currentWarning"]["severityLevel"]
                )
            else:
                data_item["risk_level"] = 0
            areas[data_item["name"]] = data_item
        return areas

    async def async_get_data(self):
        """Request processed data from the endpoint"""
        raw_data = await self.async_raw_get_data()

        return self.process_data(raw_data)
