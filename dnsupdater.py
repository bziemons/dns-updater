import pathlib
import re
from abc import abstractmethod, ABC

SUBDOMAIN = "^\w((\w|\-)*\w)?\."
DATABASE_LOCATION = "/srv/dns/zones/"


class DnsUpdater(ABC):
    @abstractmethod
    def set_ip_for_domain(self, domain: str, ip: str):
        return NotImplemented


class BindUpdater(DnsUpdater):
    _database_location = pathlib.Path(DATABASE_LOCATION)
    _domain_map = {
        SUBDOMAIN + "ch94.de": "ch94.de.db"
    }

    def __init__(self):
        regexlist = list(self._domain_map.keys())
        for pattern in regexlist:
            try:
                re.template(pattern)
            except Exception as e:
                raise RuntimeError("Error when parsing domain pattern " + pattern) from e

    def set_ip_for_domain(self, domain: str, ip: str):
        print("STUB setting ip " + ip + " for domain " + domain)

