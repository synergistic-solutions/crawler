import ssl
import socket

from synergistic.crawler import HTTPClient


class HTTPSClient(HTTPClient, ssl.SSLObject):

    def __init__(self, hostname: str = None, port: int = 80, path: str = ''):
        self.socket = socket.socket()

        context = ssl.SSLContext(ssl.PROTOCOL_TLS)
        context.verify_mode = ssl.CERT_NONE

        self.wrapped_socket = context.wrap_socket(
            sock=self.socket, server_side=False,
            do_handshake_on_connect=True,
            suppress_ragged_eofs=True
        )

        self.wrapped_socket.settimeout(1)
        try:
            self.connect((hostname, port))
            self._closed = False
        except:
            self._closed = True
        self.wrapped_socket.settimeout(0)

        if not path.startswith('/'):
            path = '/' + path

        self.path = path
        self.host = hostname

        self.buffer = b''

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
