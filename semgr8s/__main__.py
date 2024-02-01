import logging

from apscheduler.schedulers.background import BackgroundScheduler

from semgr8s.app import APP
from semgr8s.updater import update_rules

if __name__ == "__main__":
    APP.logger.addHandler(logging.StreamHandler())
    APP.logger.setLevel(logging.DEBUG)

    scheduler = BackgroundScheduler()
    job = scheduler.add_job(update_rules, "interval", minutes=1)
    scheduler.start()

    # first run at start up
    update_rules()

    APP.run(
        ssl_context=("/app/certs/ca.crt", "/app/certs/ca.key"),
        port=5000,
        host="0.0.0.0",
        debug=True,
    )
