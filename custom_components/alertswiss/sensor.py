import logging
import async_timeout
from datetime import datetime
from homeassistant.helpers.entity import Entity
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE

_LOGGER = logging.getLogger(__name__)

DEFAULT_RADIUS = 10  # km

async def async_setup_platform(hass, config, add_entities, discovery_info=None):
    lat = config.get(CONF_LATITUDE, hass.config.latitude)
    lon = config.get(CONF_LONGITUDE, hass.config.longitude)
    radius = config.get("radius", DEFAULT_RADIUS)

    add_entities([AlertSwissSensor(hass, lat, lon, radius)], True)

class AlertSwissSensor(Entity):
    def __init__(self, hass, lat, lon, radius):
        self._hass = hass
        self._lat = lat
        self._lon = lon
        self._radius = radius
        self._state = None
        self._attributes = {}

    @property
    def name(self):
        return "AlertSwiss Warnungen"

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._attributes

    async def async_update(self):
        url = "https://www.alertswiss.ch/de/feeds/alert_rss.xml"
        try:
            async with async_timeout.timeout(10):
                session = self._hass.helpers.aiohttp_client.async_get_clientsession()
                resp = await session.get(url)
                text = await resp.text()
        except Exception as err:
            _LOGGER.error("Fehler beim Abruf: %s", err)
            return

        # RSS parsen (z.B. mit xml.etree.ElementTree)
        import xml.etree.ElementTree as ET
        root = ET.fromstring(text)

        warnings = []
        for item in root.findall(".//item"):
            # Geokoordinaten extrahieren, Beispiel <geo:lat>, <geo:long>
            lat = float(item.findtext("{http://www.georss.org/georss}point").split()[0])
            lon = float(item.findtext("{http://www.georss.org/georss}point").split()[1])
            title = item.findtext("title")
            pub_date = item.findtext("pubDate")

            # Distanzberechnung (Haversine)
            from math import radians, cos, sin, asin, sqrt
            def haversine(lat1, lon1, lat2, lon2):
                R = 6371
                dlat = radians(lat2 - lat1)
                dlon = radians(lon2 - lon1)
                a = sin(dlat/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(dlon/2)**2
                return R * 2 * asin(sqrt(a))

            dist = haversine(self._lat, self._lon, lat, lon)
            if dist <= self._radius:
                warnings.append({
                    "title": title,
                    "distance_km": round(dist, 1),
                    "published": pub_date
                })

        self._state = len(warnings)
        self._attributes = {"alerts": warnings}
