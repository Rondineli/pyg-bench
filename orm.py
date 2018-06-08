from sqlalchemy import create_engine
from sqlalchemy.exc import InternalError
from prettytable import PrettyTable
from render import RenderTemplates
from redis_queue import RedisQueue
from count import CountResults

import os
import time
import random
import uuid
import datetime
import argparse
import threading
import configparser


class ReportCharts(object):

    def __init__(self, time_execution_in_sec, title, config, slave=False):

        t = RenderTemplates()
        data = {
            "time_execution_in_sec": time_execution_in_sec,
            "title": title
        }

        if not slave:
            output = t.render(data=data)
            nuuid = str(uuid.uuid4())
            file_chart_temp = "/tmp/{}.html".format(nuuid)
            new_html_template = open(file_chart_temp, "w")
            new_html_template.write(output)
            new_html_template.close()
            thr = threading.Thread(
                target=t.start_report,
                args=(
                    data,
                    config,
                    file_chart_temp
                )
            )
            thr.daemon = True
            thr.start()

    def update_chart(self, queue, chart_id, serie, data):

        data = {
            "chart_id": chart_id,
            "data": {
                "serie": serie,
                "data": data
            }
        }
        queue.put(data)


class MyTaskSet(CountResults):

    def __init__(self, time_execution_in_sec, chart_title,
                 slave, config, *args, **kwargs):
        self.running = True
        self.slave = slave

        redis_kwargs = {
            "host": config["redis"]["redis_host"],
            "port": config["redis"]["redis_port"],
            "db": config["redis"]["redis_db"]
        }
        self.queue_chart = RedisQueue(
            name="data_chart",
            namespace="data_chart",
            **redis_kwargs
        )
        self.queue_tasks = RedisQueue(
            name="data_tasks",
            namespace="data_tasks",
            **redis_kwargs
        )
        self.chart = ReportCharts(
            time_execution_in_sec,
            chart_title,
            config,
            self.slave
        )
        self.db = create_engine(config["database"]["db_string"])
        super(MyTaskSet, self).__init__(time_execution_in_sec, chart_title,
                                        slave, config, *args, **kwargs)

    def purge_queues(self):
        self.queue_chart.purge()
        self.queue_tasks.purge()
        self.queue_data.purge()

    def set_tasks(self):
        while self.running:
            self.queue_tasks.put("heartbeat")

    def vacuum(self):
        try:
            self.db.execute("vacuum analyze films;")
            self.db.execute("vacuum films;")

        except InternalError:
            from table import Films
            films = Films()
            films.metadata.create_all(bind=self.db)
        return

    def read(self):
        while self.running and self.queue_tasks.get():
            ts = datetime.datetime.now()
            self.db.execute("SELECT * FROM films;".format(
                str(uuid.uuid4())[-5:], random.randint(0, self.LIMIT * 100))
            )
            te = datetime.datetime.now()
            ms = ts - te
            self.queue_data.put(
                {
                    "type": "select",
                    "total_seconds": round(ms.total_seconds() * -1, 5)
                }
            )

    def write(self):
        while self.running and self.queue_tasks.get():
            # INSERTS
            code = str(uuid.uuid4())[-5:]
            ts = datetime.datetime.now()
            self.db.execute(
                "INSERT into films (code, title, did, kind) VALUES('{}', 'test', {}, 't');".format( # noqa
                    code,
                    random.randint(0, self.LIMIT * 100)
                )
            )
            te = datetime.datetime.now()
            ms = ts - te
            self.queue_data.put(
                {
                    "type": "insert",
                    "total_seconds": round(ms.total_seconds() * -1, 5)
                }
            )

            # UPDATES
            new_code = str(uuid.uuid4())[-5:]
            ts = datetime.datetime.now()
            self.db.execute(
                "UPDATE films set code='{}' where code='{}';".format(
                    new_code,
                    code
                )
            )
            te = datetime.datetime.now()
            ms = ts - te
            self.queue_data.put(
                {
                    "type": "update",
                    "total_seconds": round(ms.total_seconds() * -1, 5)
                }
            )

    def on_finish(self):
        self.running = False
        time.sleep(5)
        print("Getting time here to wait all queue get empty")

        while self.queue_data.qsize() > 0 or self.queue_chart.qsize() > 0:
            print("Waiting finishing all pendents query")
            time.sleep(1)

        if not self.slave:
            self.chart.update_chart(
                self.queue_chart,
                2,
                "select",
                data=self.RESPONSE_TIME_AVERAGE["average_select"]
            )
            self.chart.update_chart(
                self.queue_chart,
                2,
                "update",
                data=self.RESPONSE_TIME_AVERAGE["average_update"]
            )
            self.chart.update_chart(
                self.queue_chart,
                2,
                "insert",
                data=self.RESPONSE_TIME_AVERAGE["average_insert"]
            )
            self.chart.update_chart(
                self.queue_chart,
                3,
                "select",
                data=self.SELECTS_COUNT
            )
            self.chart.update_chart(
                self.queue_chart,
                3,
                "update",
                data=self.UPDATES_COUNT
            )
            self.chart.update_chart(
                self.queue_chart,
                3,
                "insert",
                data=self.INSERTS_COUNT
            )

            table = PrettyTable([
                "Item",
                "Total",
                "Average Execution (sec)",
                "Total Executed (sec)"
            ])

            table.add_row([
                "INSERTS",
                self.INSERTS_COUNT,
                self.RESPONSE_TIME_AVERAGE["average_insert"],
                ""

            ])
            table.add_row([
                "UPDATES",
                self.UPDATES_COUNT,
                self.RESPONSE_TIME_AVERAGE["average_update"],
                ""

            ])
            table.add_row([
                "SELECTS",
                self.SELECTS_COUNT,
                self.RESPONSE_TIME_AVERAGE["average_select"],
                ""

            ])
            table.add_row([
                "",
                "",
                "",
                "Finished execution after {} seconds".format(self.TIMING)

            ])

            print(table)

        while self.queue_data.qsize() > 0 or self.queue_chart.qsize() > 0:
            print("Waiting finishing all pendents query")
            time.sleep(1)

        self.purge_queues()

        print("Finished! See http://localhost:9111/ to full report")
        os._exit(0)


class RealTimeChart(MyTaskSet):
    def __init__(self, time_execution_in_sec, chart_title,
                 slave, config, *args, **kwargs):
        super(RealTimeChart, self).__init__(time_execution_in_sec, chart_title,
                                            slave, config, *args, **kwargs)

    def do_run(self):
        while self.running:
            ts = datetime.datetime.now()
            self.chart.update_chart(
                self.queue_chart,
                1,
                "select",
                data={
                    "x": float(ts.timestamp()) * 1000.0,
                    "y": self.RESPONSE_TIME_AVERAGE["average_select"]
                }
            )
            self.chart.update_chart(
                self.queue_chart,
                1,
                "update",
                data={
                    "x": float(ts.timestamp()) * 1000.0,
                    "y": self.RESPONSE_TIME_AVERAGE["average_update"]
                }
            )
            self.chart.update_chart(
                self.queue_chart,
                1,
                "insert",
                data={
                    "x": float(ts.timestamp()) * 1000.0,
                    "y": self.RESPONSE_TIME_AVERAGE["average_insert"]
                }
            )
            time.sleep(20)


def main():

    description = 'Tests suites for postgresql'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        '--config-file', help='config file path',
        required=True
    )
    parser.add_argument(
        '--slave',
        help='Set type of tasks executions',
        required=False,
        action='store_true',
        default=False
    )

    parser.add_argument(
        '--send-tasks',
        help='Set type of tasks executions',
        required=False,
        action='store_true',
        default=True
    )

    parser.add_argument(
        '--interval',
        help='Interval tha will run the tests',
        required=True
    )

    parser.add_argument(
        '--title',
        help='Title of thet dashboard',
        required=True
    )
    parser.add_argument(
        '--threads',
        help='Paralelal Executions',
        required=True
    )

    args, extra_params = parser.parse_known_args()

    config = configparser.ConfigParser()
    config.read(args.config_file)

    real_time = RealTimeChart(
        int(args.interval),
        args.title,
        args.slave,
        config
    )
    real_time.purge_queues()
    real_time.vacuum()

    if args.send_tasks:
        for item in range(0, int(args.threads)):
            tasks = threading.Thread(target=real_time.set_tasks)
            tasks.daemon = True
            tasks.start()

    if not args.slave:
        run = threading.Thread(target=real_time.do_run)
        run.daemon = True
        run.start()

        count = threading.Thread(target=real_time.do_count)
        count.daemon = True
        count.start()

    for item in range(0, int(args.threads)):
        read = threading.Thread(target=real_time.read)
        write = threading.Thread(target=real_time.write)
        read.daemon = True
        write.daemon = True
        read.start()
        write.start()

    try:
        time.sleep(int(args.interval))
    except (KeyboardInterrupt, SystemExit):
        print("Cleaning everything...")

    real_time.on_finish()
