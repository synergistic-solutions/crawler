import socket


class HTTPClient(socket.socket):

    user_agent = "SearchBot/0.0"
    callback = None

    def __init__(self, hostname: str = None, port: int = 80, path: str = ''):
        socket.socket.__init__(self)
        self.settimeout(3)

        try:
            self.connect((hostname, port))
            self._closed = False
        except:
            self._closed = True

        if not path.startswith('/'):
            path = '/' + path
        self.path = path
        self.host = hostname

        self.buffer = b''
        self._closed = False

    def on_receive(self):
        message = self.recv(4096)
        print(message)
        if not message:
            self.close()
            return
        self.buffer += message
        self.handle_message(self.buffer)

    def handle_message(self, message):
        try:
            message = message.decode('utf-8')
        except UnicodeDecodeError:
            print("ERROR", message)
        if self.callback:
            self.callback(self.host, self.path, message)

    def on_connect(self):
        request = "GET " + self.path + " HTTP/1.1\r\n"
        request += "Host: " + self.host + "\r\n"
        request += "User-Agent: " + self.user_agent + "\r\n"
        request += "Accept: */*\r\n"
        #request += "Connection: keep-alive\r\n"
        request += "\r\n"

        request = request.encode('utf-8')
        try:
            self.send(request)
        except:
            self._closed = True
            pass
