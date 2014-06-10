#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, json, struct, logging, traceback, socket, select, time

import gevent
from gevent import monkey;monkey.patch_all()
from gevent.queue import Queue, Empty
from gevent.event import AsyncResult
from config import logger

REQUEST_TIMEOUT = 30

class JsClient(object):
    def __init__(self, addr):
        self.addr = addr
        self.sock = None

        self.sessions = {}
        self.session_id = 0
        # spawn two greenlet
        self.write_buf = []
        self.read_buf = ""

        gevent.spawn(self._check_timeout)

    def _gen_session(self):
        if self.session_id > 0xffffffff:
            self.session_id = 1
        self.session_id += 1
        return self.session_id

    def _wait(self, session):
        ev = AsyncResult()
        self.sessions[session] = (ev, time.time())
        return ev.get()

    def _wakeup(self, session, payload):
        v = self.sessions.pop(session, None)
        if not v:
            return False
        v[0].set(payload)
        return True

    def _wakeup_all(self):
        to_wakeup = self.sessions.keys()
        for session in to_wakeup:
            logger.error("disconnect, wakeup session %d", session)
            self._wakeup(session, None)

    def _check_timeout(self):
        while True:
            try:
                to_wakeup = []
                now = time.time()
                for session in self.sessions:
                    _, ts = self.sessions[session]
                    if now - ts > REQUEST_TIMEOUT:
                        to_wakeup.append(session)

                for session in to_wakeup:
                    logger.error("session %d timeout, wakeup it", session)
                    self._wakeup(session, None)
            except:
                 logger.exception("check timeout failed")
            gevent.sleep(3)

    def connect(self):
        assert not self.sock
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(self.addr)
        self.sock.setblocking(0)
        gevent.spawn(self._dispatch)

    def _on_disconnected(self):
        logger.error("sock disconnected")

        # release all sessions and write buf
        try:
            self.write_buf = []
            self._wakeup_all()
        except:
            logger.exception("release all sessions failed")

        while True:
            self.sock = None
            try:
                logger.info("reconnect to (%s:%s)" % self.addr)
                self.connect()
            except:
                gevent.sleep(3)
                exc_type, exc_value, exc_traceback = sys.exc_info()
                logger.error("exception: %s", traceback.format_exception(exc_type, exc_value, exc_traceback))
                continue
            logger.info("reconnect to (%s:%s) succeed" % self.addr)
            break

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
            session = resp.get("session", None)
            payload = resp.get("payload", None)
            if self._wakeup(session, payload):
                logger.info("recv response:%d", session)
            else:
                logger.error("unknown response:%s", data)
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logger.error("exception: %s", traceback.format_exception(exc_type, exc_value, exc_traceback))
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
            select.select(rlist, wlist, [], 0.1)
        # quit only when socket disconnected
        self._on_disconnected()

    def _send(self, req):
        chunk = json.dumps(req)
        self._write(struct.pack("!H", len(chunk)) + chunk)

    def send(self, cmd, payload):
        logger.info("send %s, payload:%s", cmd, str(payload))
        req = {
                "cmd":cmd,
                "payload":payload
                }
        self._send(req)

    def call(self, cmd, payload):
        logger.info("call %s, payload:%s", cmd, str(payload))
        session = self._gen_session()
        req = {
                "session": session,
                "cmd":cmd,
                "payload":payload
                }
        self._send(req)
        logger.info("send request:%s, body:%s", session, req)
        return self._wait(session)

def main():
    addr = ("127.0.0.1", 5838)
    cli = JsClient(addr)
    cli.connect()

    print(cli.call("add", {"a":1, "b":2}))
    print(cli.call("add", {"a":10, "b":20}))
    print(cli.call("add", {"a":100, "b":200}))
    gevent.wait()
    pass

if __name__ == '__main__':
    main()

