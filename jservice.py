#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, json, struct, logging, traceback
import gevent
from gevent import monkey;monkey.patch_all()
from gevent.server import StreamServer

def add(req):
    gevent.sleep(0.1)
    print("-------------", req["a"], req["b"])
    return req["a"] + req["b"]

handles = {
        "add" : add
        }

# request: { 
#    session int
#    cmd     string
#    payload object
# }
# response: {
#    session int
#    payload object
# }
def handle_request(sock, data):
    try:
        req = json.loads(data)
        cmd = req["cmd"]
        handle = handles[cmd]
        payload = handle(req["payload"])
        resp = {
                "session" : req["session"],
                "payload" : payload
                }
        chunk = json.dumps(resp)
        sock.sendall(struct.pack("!H", len(chunk)) + chunk)
    except:
        logging.error("exception: %s", traceback.format_exception(sys.exc_type, sys.exc_value, sys.exc_traceback))
        pass
    
def handle_connection(sock, address):
    left = ""
    while True:
        buf = sock.recv(4096)
        if not buf:
            break

        left = left + buf
        while True:
            if len(left) < 2:
               break 
            plen, = struct.unpack('!H', left[:2])
            if len(left) < plen + 2:
               break 

            data = left[2:plen+2]
            left = left[plen+2:]
            gevent.spawn(handle_request, sock, data)

def on_new_connection(sock, address):
    gevent.spawn(handle_connection, sock, address)

def main():
    server = StreamServer(("127.0.0.1", 5838), on_new_connection)
    server.start()
    gevent.wait()

if __name__ == '__main__':
    main()

