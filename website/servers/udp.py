import json
import os
import socket
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'progress.settings'
django.setup()

from django.conf import settings
from dashboard.utils import update_bar



UDP_IP, port = settings.ALT_ENDPOINTS['udp'].split(':')
UDP_PORT = int(port)

sock = socket.socket(socket.AF_INET,  # Internet
                     socket.SOCK_DGRAM)  # UDP
sock.bind((UDP_IP, UDP_PORT))

while True:
    try:
        rec, addr = sock.recvfrom(2048)
        key, jdata = rec.decode('utf-8').split("\n")
        data = json.loads(jdata)
        update_bar(key, data)
    except (ValueError, json.JSONDecodeError) as e:
        print(e)

