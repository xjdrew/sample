#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask
from gevent_client import RpcClient

app = Flask(__name__)
app.debug = True
app.secret_key = '\x9c\xa7\xd4v\xd3\xc7f\x8fI\x8c_;\x1apF\xc4\xd3\xce\xde\xd0\xd1hc\xda\xbcr\xe7j\nj\xc6\x01\xcap\r\xa5(\x02\x85\x0f'
addr = ("127.0.0.1", 5838)
cli = RpcClient(addr)
cli.connect()

def add_wrapper(a,b):
    return cli.call("add", {"a":a, "b":b})

@app.route('/add/<int:a>/<int:b>')
def add(a, b):
    return str(add_wrapper(a,b))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8090)

