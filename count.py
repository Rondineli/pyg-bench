from redis_queue import RedisQueue

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
        self.LIMIT = 1000
        self.TIMING = time_execution_in_sec
        self.UPDATES_COUNT = 0
        self.INSERTS_COUNT = 0
        self.SELECTS_COUNT = 0
        self.RESPONSE_TIME_AVERAGE = {
            "insert": 0,
            "update": 0,
            "select": 0,
            "average_select": 0,
            "average_insert": 0,
            "average_update": 0
        }

    def do_count(self):
        while True:
            data = self.queue_data.get().decode("utf-8")
            data = data.replace("\'", "\"")
            data = json.loads(data)
            if data:
                if data["type"] == "insert":
                    self.INSERTS_COUNT += 1
                    self.RESPONSE_TIME_AVERAGE["insert"] += data["total_seconds"] # noqa
                    self.RESPONSE_TIME_AVERAGE["average_insert"] = self.RESPONSE_TIME_AVERAGE["insert"] / self.INSERTS_COUNT # noqa

                elif data["type"] == "select":
                    self.SELECTS_COUNT += 1
                    self.RESPONSE_TIME_AVERAGE["select"] += data["total_seconds"] # noqa
                    self.RESPONSE_TIME_AVERAGE["average_select"] = self.RESPONSE_TIME_AVERAGE["select"] / self.SELECTS_COUNT # noqa

                elif data["type"] == "update":
                    self.UPDATES_COUNT += 1
                    self.RESPONSE_TIME_AVERAGE["update"] += data["total_seconds"] # noqa
                    self.RESPONSE_TIME_AVERAGE["average_update"] = self.RESPONSE_TIME_AVERAGE["update"] / self.UPDATES_COUNT # noqa

                else:
                    NotfoundExcpetion("item not found!")

        time.sleep(30)
