"""
Dedicated server script for transfer txt or bin info between some computers
Author: Streltsov Sergey (c) 2017 mailto:straltsou.siarhei@gmail.com
requre lib: autobahn, twisted, requests
ip address - autodetect
port - 9999 (if need, change PORT variable
start: python3 tw2_server.py
port 9999 must be opened on the system to connect from the outside
test server on: 107.181.174.126:9999
"""

import sys
from requests import get
from twisted.python import log
from twisted.internet import reactor
from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol

PORT = 9999


class WebSockServerProtocol(WebSocketServerProtocol):
    def onConnect(self, request):
        print("Client connecting: {0}".format(request.peer))

    def onOpen(self):
        self.factory.register(self)
        print("Client connected from: {0} as: {1}".format(self.peer, self.peer))

    def connectionLost(self, reason):
        self.factory.unregister(self)
        print("Client disconnected: {0}".format(self.peer))

    def onMessage(self, payload, isBinary):
        self.factory.communicate(self, payload, isBinary)
        print("Client {0} sending message: {1}".format(self.peer, payload))


class PeerConnectorFactory(WebSocketServerFactory):
    def __init__(self, *args, **kwargs):
        super(PeerConnectorFactory, self).__init__(*args)
        self.clients = []

    def register(self, client):
            self.clients.append({'client-peer': client.peer, 'client': client})

    def unregister(self, client):
        for c in self.clients:
            if c['client-peer'] == client.peer: self.clients.remove(c)

    def communicate(self, client, payload, isBinary):
        for i, c in enumerate(self.clients):
            if c['client'] == client:
                id = i
                break
        for c in self.clients:
            msg = 'Client {0}: {1}'.format(str(id + 1), payload.decode('utf-8'))
            c['client'].sendMessage(str.encode(msg))


if __name__ == "__main__":
    log.startLogging(sys.stdout)

    ip = get('https://api.ipify.org').text
    # ip = '127.0.0.1'

    factory = PeerConnectorFactory(u'ws://' + ip + ':' + str(PORT))
    factory.protocol = WebSockServerProtocol
    factory.log.info('Server started on {host}', host=factory.host)

    reactor.listenTCP(PORT, factory)
    reactor.run()