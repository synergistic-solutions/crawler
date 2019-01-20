import ssl
import socket

from bs4 import BeautifulSoup

from synergistic import poller, broker, indexer

USER_AGENT = "Search Bot"

LIMIT = 10

queue = ["www.brookes.ac.uk"]

poller = poller.Poll(catch_errors=False)
broker = broker.client.Client("127.0.0.1", 8891, broker.Type.CRAWLER)


def add(channel, msg_id, payload):
    queue.append(payload['url'])


broker.subscribe('crawl', add)

poller.add_client(broker)


class Client(ssl.SSLObject):

    def __init__(self, url):
        self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)

        if '/' not in url:
            url += '/'
        self.HOST, self.PATH = url.split('/', 1)

        context = ssl.SSLContext(ssl.PROTOCOL_TLS)
        context.verify_mode = ssl.CERT_NONE

        self.wrapped_socket = context.wrap_socket(
            sock=self.socket, server_side=False,
            do_handshake_on_connect=True,
            suppress_ragged_eofs=True
        )

        self.connect((self.HOST, 443))

        self.buffer = b''
        self._closed = False

    def fileno(self):
        return self.wrapped_socket.fileno()

    def recv(self, *args):
        return self.wrapped_socket.recv(*args)

    def send(self, *args):
        return self.wrapped_socket.send(*args)

    def connect(self, *args):
        return self.wrapped_socket.connect(*args)

    def is_closed(self):
        return self.wrapped_socket._closed

    def close(self):
        return self.wrapped_socket.close()

    def on_receive(self):
        message = self.recv(4096)
        if not message:
            self.close()
            return
        self.buffer += message
        self.handle_message(self.buffer)

    def handle_message(self, message):
        message = message.decode('utf-8')

        soup = BeautifulSoup(message)

        # kill all script and style elements
        for script in soup(["script", "style"]):
            script.extract()  # rip it out

        # get text
        text = soup.get_text()

        # break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)

        broker.publish('index', {'url': self.HOST + '/' + self.PATH, 'content': text})

    def on_connect(self):
        request = "GET /" + self.PATH + " HTTP/1.1\r\n"
        request += "Host: " + self.HOST + "\r\n"
        request += "User-Agent: " + USER_AGENT + "\r\n"
        request += "Accept: */*\r\n"
        request += "Connection: keep-alive\r\n"
        request += "\r\n"

        request = request.encode('utf-8')
        print(request)
        self.send(request)


while True:
    urls = queue[:LIMIT]
    queue = queue[LIMIT:]
    for url in urls:
        client = Client(url)
        poller.add_client(client)
    poller.serve_once()

