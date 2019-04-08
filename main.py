from synergistic import poller, broker, crawler

LIMIT = 10

queue = ["jacob.culley.me"]

poll = poller.Poll(catch_errors=False)
broker_client = broker.Client("127.0.0.1", 8891, broker.Type.CRAWLER)


def add(channel, msg_id, payload):
    print(payload)
    queue.append(payload)


broker_client.subscribe('crawl', add)
poll.add_client(broker_client)


def parse_headers(headers):
    headers_dict = {}
    for header in headers.split('\r\n')[1:]:
        if header:
            key, value = header.split(':', 1)
            headers_dict[key] = value.lstrip()
    url = headers_dict.get('Location', '')
    url = url.split('://')[1]
    queue.append(url)


def callback(hostname, path, message):
    if '\r\n\r\n' in message:
        headers, html = message.split('\r\n\r\n', 1)
    else:
        headers, html = message, ''

    if 'Location:' in headers:
        parse_headers(headers)
    else:
        broker_client.publish()


while True:
    if not queue:
        poll.serve_once()

    try:
        url = queue[0]
        queue = queue[1:]
    except:
        continue

    if '/' in url:
        hostname, path = url.split('/', 1)
    else:
        hostname = url
        path = '/'

    client = crawler.HTTPClient(hostname, 443, path)
    client.callback = callback
    poll.add_client(client)

    poll.serve_once()
