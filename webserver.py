import http.server

import sys

import dnsupdater

__version__ = "0.1"


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
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()
    finally:
        print("Server closing")


class RequestHandler(http.server.BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        super().__init__(request, client_address, server)
        self.server_version = "RS485-DNS/" + __version__

    def do_GET(self):
        print()
        print("Got", self.command, "from", self.client_address)
        print("Request:", self.requestline)
        print("Headers:")
        print("--------")
        for k, v in self.headers.items():
            print(str(k) + ":", v)
        print()
        try:
            updater.set_ip_for_domain("test.ch94.de", "ip")
        except dnsupdater.UnknownDomainError:
            self.send_error(404, "Given domain not found")
            return

        self.send_error(500, "Not implemented")
        self.close_connection = True


if __name__ == "__main__":
    updater = dnsupdater.BindUpdater()
    main()
