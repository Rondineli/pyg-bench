from redis_queue import RedisQueue
from config import Config

import time
import json


class NotfoundExcpetion(Exception):
    pass


class CountResults(object):
    def __init__(self, time_execution_in_sec, chart_title,
                 slave, *args, **kwargs):
        self.queue_data = RedisQueue(
            name="data_count",
            namespace="data_count"
        )

        self.config = Config().get_config()

        self.LIMIT = 1000
        self.TIMING = time_execution_in_sec

        self.RESPONSE_TIME_AVERAGE = {
            "errors": 0,
            "count": {
                "insert": 0,
                "update": 0,
                "select": 0
            },
            "average": {
                "select": 0,
                "insert": 0,
                "update": 0
            },
            "count_seconds": {
                "insert": 0,
                "update": 0,
                "select": 0
            }
        }

    def do_count(self):
        while True:
            data = self.queue_data.get().decode("utf-8")
            data = data.replace("\'", "\"")
            data = json.loads(data)
            if data:
                self.RESPONSE_TIME_AVERAGE["count"][data["type"]] += 1

                self.RESPONSE_TIME_AVERAGE["count_seconds"][data["type"]] += data["total_seconds"] # noqa
                self.RESPONSE_TIME_AVERAGE["average"][data["type"]] = self.RESPONSE_TIME_AVERAGE["count_seconds"][data["type"]] / self.RESPONSE_TIME_AVERAGE["count"][data["type"]] # noqa

        time.sleep(30)
