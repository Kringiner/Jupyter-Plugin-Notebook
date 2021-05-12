from jupyter_server.base.handlers import JupyterHandler
from jupyter_server.extension.handler import ExtensionHandlerMixin
import json


class DefaultHandler(ExtensionHandlerMixin, JupyterHandler):
    def get(self):
        obj = {'key': 'value'}
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(obj))
