DOMAIN = "eafa"
DOMAIN_DATA = f"{DOMAIN}_data"
NAME = "Environment Agency (UK) Flood Alerts"
VERSION = "0.1"

# Platforms
SENSOR = "sensor"
PLATFORMS = [SENSOR]

CONF_LATITUDE = "latitude"
CONF_LONGITUDE = "longitude"
CONF_DISTANCE = "distance"

SEVERITY_LEVEL = {
    "Severe Flood Warning": 1,
    "Flood Warning": 2,
    "Flood Alert": 3,
    "Warning no Longer in Force": 4,
}

REFRESH = 15
