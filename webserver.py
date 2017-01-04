import base64
import binascii
import http.server
import ipaddress
import signal
import sys
import threading
from urllib.parse import urlparse, parse_qs

import dnsupdater

VERSION = "0.1"
ACCEPTED_AUTH = "Basic"


def main():
    if len(sys.argv) < 2:
        print("No port given for the webserver, using 8080", file=sys.stderr)
        port = 8080
    else:
        try:
            port = int(sys.argv[1])
        except Exception as e:
            raise RuntimeError("Something was wrong with the port: " + sys.argv[1]) from e

    httpd = http.server.HTTPServer(("", port), RequestHandler)
    print("Serving at port", port)
    main_thread = threading.get_ident()

    def sigterm_handler(signum, frame):
        print("Shutting down...")
        signal.pthread_kill(main_thread, signal.SIGINT)

    signal.signal(signal.SIGTERM, sigterm_handler)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()
    finally:
        print("Server shut down")


class RequestHandler(http.server.BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        super().__init__(request, client_address, server)

    def version_string(self):
        return "RS485-DDNS/" + VERSION + " " + sys.version

    def send_head(self):
        auth_header = self.headers['Authorization']
        if auth_header is None:
            self.send_unauthorized()
            return

        if not auth_header.startswith(ACCEPTED_AUTH + " "):
            self.send_unauthorized("Unknown authorization method")
            return

        encoded_auth = auth_header[len(ACCEPTED_AUTH) + 1:]

        try:
            auth_string = base64.standard_b64decode(encoded_auth).decode()
        except (binascii.Error, ValueError, UnicodeDecodeError):
            self.send_error(400, "Error when decoding authentication string")
            return

        splitter = auth_string.find(':')
        if splitter == -1:
            self.send_error(400, "Error when decoding authentication string")
            return

        username = auth_string[:splitter]
        password = auth_string[splitter + 1:]

        if username == "user" and password == "pass":
            parsedurl = urlparse(self.path)

            if parsedurl.path != "/update":
                self.send_error(404)
                return

            try:
                query_dict = parse_qs(parsedurl.query)
            except Exception:
                self.send_error(400, "Could not parse query")
                return

            if 'domain' not in query_dict:
                self.send_error(400, "No domain given")
                return

            if 'ipaddr' not in query_dict and 'ip6addr' not in query_dict:
                self.send_error(400, "No ip address given")
                return

            ip4 = query_dict.get('ipaddr', (None,))[0]
            ip6 = query_dict.get('ip6addr', (None,))[0]

            if ip4 is not None:
                try:
                    ip4 = ipaddress.IPv4Address(ip4)
                except ipaddress.AddressValueError:
                    self.send_error(400, "IPv4 address invalid")

            if ip6 is not None:
                try:
                    ip6 = ipaddress.IPv6Address(ip6)
                except ipaddress.AddressValueError:
                    self.send_error(400, "IPv6 address invalid")

            try:
                updater.set_record_for_domain(query_dict['domain'][0], ip4, ip6)
            except dnsupdater.UnknownDomainError:
                self.send_error(404, "Given domain not found")
                return
            except dnsupdater.UserDomainError:
                self.send_error(409, "Given domain is a user configured domain")
                return

            self.send_response(200, "DNS updated")
            self.end_headers()
        else:
            self.send_unauthorized()

    def send_unauthorized(self, message=None):
        self.send_response(401, message)
        self.send_header('WWW-Authenticate', ACCEPTED_AUTH)
        self.end_headers()
        # no body

    def do_GET(self):
        self.send_head()

    def do_HEAD(self):
        self.send_head()


if __name__ == "__main__":
    updater = dnsupdater.BindUpdater()
    main()
