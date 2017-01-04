import ipaddress
import pathlib
import re
from abc import abstractmethod, ABC

SUBDOMAIN = r"^\w((\w|\-)*\w)?\."
DATABASE_LOCATION = "/srv/dns/zones/"


class DnsUpdater(ABC):
    @abstractmethod
    def set_record_for_domain(self, domain: str, ip4: ipaddress.IPv4Address = None, ip6: ipaddress.IPv6Address = None):
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
                re.compile(pattern)
            except Exception as e:
                raise RuntimeError("Error when parsing domain pattern " + pattern) from e

    def set_record_for_domain(self, domain: str, ip4: ipaddress.IPv4Address = None, ip6: ipaddress.IPv6Address = None):
        match = None
        for pattern, filename in self._domain_map.items():
            if re.match(pattern, domain):
                match = filename
                break

        if match is None:
            raise UnknownDomainError(domain)

        # TODO
        raise UserDomainError(domain)


class UnknownDomainError(Exception):
    def __init__(self, domain: str):
        super().__init__("Unknown domain: " + domain)


class UserDomainError(Exception):
    def __init__(self, domain: str):
        super().__init__("Domain is a user domain: " + domain)
