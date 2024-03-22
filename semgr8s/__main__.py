"""
Main method starting the web server.
"""

import logging

from apscheduler.schedulers.background import BackgroundScheduler
from cheroot.server import HTTPServer
from cheroot.wsgi import Server
from cheroot.ssl.builtin import BuiltinSSLAdapter

from semgr8s.app import APP
from semgr8s.updater import update_rules

if __name__ == "__main__":
    APP.logger.setLevel(logging.DEBUG)

    scheduler = BackgroundScheduler()
    job = scheduler.add_job(update_rules, "interval", minutes=1)
    scheduler.start()

    # first run at start up
    update_rules()

    HTTPServer.ssl_adapter = BuiltinSSLAdapter(
        certificate="/app/certs/tls.crt", private_key="/app/certs/tls.key"
    )
    server = Server(("0.0.0.0", 5000), APP)
    server.start()
