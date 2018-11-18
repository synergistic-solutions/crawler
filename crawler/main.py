import socket

import poller

USER_AGENT = "Search Bot"

queue = ["stallman.org", "culley.me"]

poller = poller.Poll(catch_errors=False)


class Client(socket.socket):

    def __init__(self, url):
        socket.socket.__init__(self, family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        if '/' not in url:
            url += '/'
        self.HOST, self.PATH = url.split('/', 1)

        self.connect((self.HOST, 80))

        self.buffer = b''
        self._closed = False

    def is_closed(self):
        return self._closed

    def on_message(self):
        message = self.recv(4096)
        if not message:
            self.close()
            return

        self.buffer += message
        if message.endswith(b'\r\n'):
            self.handle_message(self.buffer)
            self.buffer = b''

    def handle_message(self, message):
        print(message)

    def on_connect(self):
        request = "GET /" + self.PATH + " HTTP/1.1\r\n"
        request += "Host: " + self.HOST + "\r\n"
        request += "User-Agent: " + USER_AGENT + "\r\n"
        request += "Accept: */*\r\n"
        request += "Connection: keep-alive\r\n"
        request += "\r\n"

        request = request.encode('utf-8')
        self.send(request)


def crawl():
    while True:
        for url in queue:
            client = Client(url)
            poller.add_client(client)
        queue.clear()
        poller.serve_once()

crawl()
