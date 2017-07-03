"""
Client script for transfer (send/receive) txt or bin info between some computers
Author: Streltsov Sergey (c) 2017 mailto:straltsou.siarhei@gmail.com
requre lib: autobahn, twisted, requests
ip address - prompt to enter
port - prompt to enter
role - (S)ender - to send info, (R)eceiver - to receive info
start: python3 tw2_client_uni.py
the client can be behind NAT
test server on: 107.181.174.126:9999
"""

import sys
from twisted.python import log
from twisted.internet import reactor
from autobahn.twisted.websocket import WebSocketClientProtocol
from autobahn.twisted.websocket import WebSocketClientFactory


class MyClientProtocol(WebSocketClientProtocol):
    def __init__(self, *args, **kwargs):
        super(MyClientProtocol, self).__init__(*args)

    def onConnect(self, response):
        print('Connected to server: {0}, as: {1}'.format(response.peer, self.role))

    def onOpen(self):
        print('WebSocket connection open.')

        def process_msg():
            print('Input message, Exit - to stay a receiver: ')
            msg = input()
            if msg == 'Exit':
                self.role = 'rcv'
                log.msg('Now you are the receiver.')
                return 1
            self.sendMessage(msg.encode('utf-8'))
            self.factory.reactor.callLater(1, process_msg)

        if self.role == 'snd':
            process_msg()

    def onMessage(self, payload, isBinary):
        if self.role == 'rcv':
            if isBinary:
                print("Binary message received: {0} bytes".format(len(payload)))
            else:
                print("Text message received: {0}".format(payload.decode('utf8')))

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))


if __name__ == '__main__':
    log.startLogging(sys.stdout)

    log.msg('Input dedicated server ip address (xxx.xxx.xxx.xxx): ')
    ip = input()
    # ip = '107.181.174.126'
    log.msg('Input dedicated server connection port: ')
    port = int(input())
    # port = 9999
    log.msg('Enter client role: (S)ender or (R)eceiver: ')
    role = input()[0].upper()
    if role == 'S':
        role = 'snd'
    elif role == 'R':
        role = 'rcv'
    else:
        log.msg('Error in select role/ restart client')
        sys.exit(1)

    factory = WebSocketClientFactory(u'ws://' + ip + ':' + str(port))
    MyClientProtocol.role = role
    factory.protocol = MyClientProtocol

    reactor.connectTCP(ip, port, factory)
    reactor.run()