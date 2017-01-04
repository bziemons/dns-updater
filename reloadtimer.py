import pathlib
import subprocess
import sys

CACHE_LOCATION = "."
DNS_DATABASE_LOCATION = "/docker/etc/adns/zones/"
DNS_RELOAD_COMMAND = ("systemctl", "restart", "adns")


def main():
    p = pathlib.Path(DNS_DATABASE_LOCATION)

    if not p.exists():
        print("DNS Database location does not exist:", DNS_DATABASE_LOCATION, file=sys.stderr)

    if haschanged(p):
        reloaddns()


def haschanged(p: pathlib.Path) -> bool:
    cache = pathlib.Path(CACHE_LOCATION)
    if not cache.exists():
        raise RuntimeError("Cache location does not exist: " + str(cache))

    return True


def reloaddns():
    subprocess.run(*DNS_RELOAD_COMMAND)


if __name__ == "__main__":
    main()
