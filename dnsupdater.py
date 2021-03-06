import codecs
import ipaddress
import subprocess
from abc import abstractmethod, ABC

NSUPDATE_KEY_LOCATION = "/srv/dns/Khelios.rs485.network.+165+63000.private"
NSUPDATE_CMDLINE = ["nsupdate", "-v", "-k", NSUPDATE_KEY_LOCATION]


class DnsUpdater(ABC):
    @abstractmethod
    def set_record_for_domain(self, domain: str, ip4: ipaddress.IPv4Address = None, ip6: ipaddress.IPv6Address = None):
        return NotImplemented


class BindUpdater(DnsUpdater):
    def set_record_for_domain(self, domain: str, ip4: ipaddress.IPv4Address = None, ip6: ipaddress.IPv6Address = None):
        if 'dyndns' in domain:
            raise UnconfigurableDomainError(domain)

        nsupdate_lines = list()
        nsupdate_lines.append("update delete " + domain + " AAAA\n")
        nsupdate_lines.append("update delete " + domain + " A\n")
        if ip6 is not None:
            nsupdate_lines.append("update add " + domain + " 60 IN AAAA " + str(ip6) + "\n")
        if ip4 is not None:
            nsupdate_lines.append("update add " + domain + " 60 IN A " + str(ip4) + "\n")
        nsupdate_lines.append("send\n")

        nsupdate_bytelines = list(map(lambda s: codecs.encode(s), nsupdate_lines))
        print("STDIN::\n", nsupdate_bytelines)

        pipe = subprocess.PIPE
        with subprocess.Popen(NSUPDATE_CMDLINE, stderr=pipe, stdout=pipe, stdin=pipe) as phandle:
            phandle.stdin.writelines(nsupdate_bytelines)
            phandle.stdin.flush()
            stdout, stderr = phandle.communicate(timeout=10)
            if len(stdout) != 0:
                stdout_output = codecs.decode(stdout)
                print("NSUPDATE::\n", stdout_output)
            phandle.stdin.close()

            if len(stderr) != 0:
                stderr_output = codecs.decode(stderr, errors='replace')
                raise TemporarilyUnconfigurableError(domain) from RuntimeError(stderr_output)

            try:
                phandle.wait(timeout=3)
            except subprocess.TimeoutExpired as e:
                phandle.kill()
                raise TemporarilyUnconfigurableError(domain) from e


class UnknownDomainError(Exception):
    def __init__(self, domain: str):
        super().__init__("Unknown domain: " + domain)


class TemporarilyUnconfigurableError(Exception):
    def __init__(self, domain: str):
        super().__init__("Temporarily unconfigurable domain: " + domain)


class UnconfigurableDomainError(Exception):
    def __init__(self, domain: str):
        super().__init__("Unconfigurable domain: " + domain)
