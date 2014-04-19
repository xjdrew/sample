#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, json, struct, logging, traceback, socket, select

import gevent
from gevent import monkey;monkey.patch_all()
from gevent.queue import Queue, Empty
from gevent.event import AsyncResult

class RpcClientDisconnected(BaseException):pass

class RpcClient(object):
    def __init__(self, addr):
        self.addr = addr
        self.sock = None

        self.sessions = {}
        self.session_id = 0
        # spawn two greenlet
        self.write_buf = []
        self.read_buf = ""

    def _gen_session(self):
        if self.session_id > 0xffffffff:
            self.session_id = 1
        self.session_id += 1
        return self.session_id

    def connect(self):
        assert not self.sock
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(self.addr)
        self.sock.setblocking(0)
        gevent.spawn(self._dispatch)

    def _on_disconnected(self):
        logging.error("sock disconnected")
        self.sock = None
        raise RpcClientDisconnected

    def _write(self, chunk=None):
        if not self.write_buf and not chunk:
            return False

        if chunk:
            self.write_buf.append(chunk)

        chunk = self.write_buf[0]
        sz = self.sock.send(chunk)
        if sz == 0:
            return None

        if len(chunk) == sz:
            self.write_buf.pop(0)
        else:
            self.write_buf[0] = chunk[sz:]
        return True

    def _read(self):
        try:
            buf = self.sock.recv(4096)
        except socket.error:
            return False
        if not buf:
            return None

        self.read_buf += buf
        return True

    def _dispatch_response(self):
        bufsz = len(self.read_buf) 
        if bufsz < 2:
            return False

        plen, = struct.unpack("!H", self.read_buf[:2])
        if bufsz < plen + 2:
            return False
        data = self.read_buf[2:plen+2]
        self.read_buf = self.read_buf[plen+2:]
        try:
            resp = json.loads(data)
            session = resp["session"]
            ev = self.sessions[session]
            ev.set(resp["payload"])
        except:
            logging.error("exception: %s", traceback.format_exception(sys.exc_type, sys.exc_value, sys.exc_traceback))
        return True

    def _dispatch(self):
        while True:
            rf = self._read()
            if rf == None:
                #disconnected
                break

            wf = self._write()
            df = self._dispatch_response()
            if wf or rf or df:
                continue
            rlist = [self.sock]
            wlist = []
            if wf == None:
                wlist.append(self.sock)
            select.select(rlist, wlist, None, 0.1)
        # quit only when socket disconnected
        self._on_disconnected()

    def call(self, cmd, payload):
        session = self._gen_session()
        req = {
                "session": session,
                "cmd":cmd,
                "payload":payload
                }
        chunk = json.dumps(req)
        self._write(struct.pack("!H", len(chunk)) + chunk)

        ev = AsyncResult()
        self.sessions[session] = ev
        return ev.get()

def main():
    addr = ("127.0.0.1", 5838)
    cli = RpcClient(addr)
    cli.connect()

    print(cli.call("add", {"a":1, "b":2}))
    print(cli.call("add", {"a":10, "b":20}))
    print(cli.call("add", {"a":100, "b":200}))
    gevent.wait()
    pass

if __name__ == '__main__':
    main()

