from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
import urllib.parse
import pathlib
import mimetypes
import socket
import json


LOCAL_HOST = "127.0.0.1"
SERV_PORT = 3000
CLIENT_PORT = 5000
FILE_PATH = "/home/vasya/Стільниця/P.Web-2.4/storage/data.json"


class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == "/":
            self.send_html_file("index.html")
        elif pr_url.path == "/message":
            self.send_html_file("message.html")
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file("error.html", 404)

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        with open(filename, "rb") as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", "text/plain")
        self.end_headers()
        with open(f".{self.path}", "rb") as file:
            self.wfile.write(file.read())

    def do_POST(self):
        data = self.rfile.read(int(self.headers["Content-Length"]))
        # # print(data)
        # data_parse = urllib.parse.unquote_plus(data.decode())
        # # print(data_parse)
        # data_dict = {
        #     key: value for key, value in [el.split("=") for el in data_parse.split("&")]
        # }
        # print(data_dict)
        self.send_response(302)
        self.send_info(data)
        self.send_header("Location", "/")
        self.end_headers()

    def send_info(self, data):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect((LOCAL_HOST, CLIENT_PORT))
        sock.send(data)


def run_web():
    http = HTTPServer((LOCAL_HOST, SERV_PORT), HttpHandler)
    try:
        print("Running web server...")
        http.serve_forever()
    except KeyboardInterrupt:
        print("Dont running web server...")
        http.server_close()


def run_socket():
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((LOCAL_HOST, CLIENT_PORT))
    print("Running socket server...")
    try:
        while True:
            data, address = server.recvfrom(1024)
            print(f"Received data: {data.decode()} from: {address}")
            write_to_json(data)

    except KeyboardInterrupt:
        print(f"Destroy server")
    finally:
        server.close()


def write_to_json(data):
    data_parse = urllib.parse.unquote_plus(data.decode())
    data_dict = {
        key: value for key, value in [el.split("=") for el in data_parse.split("&")]
    }
    data = {str(datetime.now()): data_dict}
    print(data)
    load_data = json.load(open(FILE_PATH))
    load_data.update(data)
    with open(FILE_PATH, "w") as fh:
        json.dump(load_data, fh, indent=4)
        print("Json file was updated")


if __name__ == "__main__":
    web_server = Thread(target=run_web)
    socket_server = Thread(target=run_socket)

    web_server.start()
    socket_server.start()

    web_server.join()
    socket_server.join()
