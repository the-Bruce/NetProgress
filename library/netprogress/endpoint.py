import json
import socket

import requests


class Endpoint:
    name = ""

    def __init__(self, response):
        if self.name not in response['endpoints']:
            raise ValueError()
        self.url = response['endpoints'][self.name]
        self.session_key = response['key']

    def update(self, pending):
        raise NotImplementedError("Please use an instantiation")

    def enter(self):
        raise NotImplementedError("Please use an instantiation")

    def exit(self):
        raise NotImplementedError("Please use an instantiation")


class Http(Endpoint):
    name = "http"

    def update(self, pending):
        data = {
            "key": self.session_key,
            "updates": json.dumps(pending)
        }
        requests.post(self.url, data=data)

    def enter(self):
        pass

    def exit(self):
        pass


class Udp(Endpoint):
    name = "udp"

    def update(self, pending):
        data = self.session_key + "\n" + json.dumps(pending)
        (ip, port) = self.url.split(':')
        self.socket.sendto(bytes(data, "utf-8"), (ip, int(port)))

    def enter(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def exit(self):
        self.socket.close()