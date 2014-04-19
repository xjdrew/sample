#!/bin/bash
python gevent_service.py &
# test: ab -n 1000 -c 100 http://127.0.0.1:8090/add/8/9

# uwsgi without gevent
#/usr/local/bin/uwsgi --http :8090 --wsgi-file web_service.py --callable app --workers 1 --master --stats :8091

# uwsgi with gevent
/usr/local/bin/uwsgi --http :8090 --wsgi-file web_service.py --callable app --gevent 100 --workers 1 --master --stats :8091

