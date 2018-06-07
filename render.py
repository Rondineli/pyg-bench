from http.server import BaseHTTPRequestHandler, HTTPServer
from redis_queue import RedisQueue

import jinja2
import os
import json

BASE_PATH = os.path.dirname(os.path.abspath(__file__))

__all__ = ["RenderTemplates"]


class Singleton(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(
                                cls, *args, **kwargs)
        return cls._instance


class WebServerClass(BaseHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        self.singleton = Singleton()
        self.queue_chart = RedisQueue(
            name="data_chart",
            namespace="data_chart"
        )
        super(WebServerClass, self).__init__(*args, **kwargs)

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):

        if self.path == "/":
            self.path = self.singleton.template_path

        self._set_headers()

        f = open(self.singleton.template_path, "rb")
        self.wfile.write(f.read())
        f.close()
        while True:
            data = self.queue_chart.get().decode("utf-8")
            data = data.replace("\'", "\"")
            data = json.loads(data)
            if data:
                self.wfile.write(
                    "<script type=\"text/javascript\">AddDataChart(chart_id={}, data={});</script>".format( # noqa
                        data["chart_id"],
                        data["data"]
                    ).encode(encoding='utf_8')
                )
        return


class RenderTemplates(object):
    def __init__(self, template=None, port=9111):
        self.singleton = Singleton()
        self.port = port
        if template is None:
            self.template_path = os.path.join(BASE_PATH, './templates/')
            self.template = "chart_report.html"

    def render(self, data):
        return jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.template_path)
        ).get_template(self.template).render(data)

    def start_report(self, data, config, template=None):
        if template is not None:
            self.singleton.template_path = template
        self.singleton.config = config
        server_address = ('', self.port)
        webd = HTTPServer(server_address, WebServerClass)
        return webd.serve_forever()
