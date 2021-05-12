import json
from abc import ABC

from notebook.base.handlers import IPythonHandler


class PrettyPythonHandler(IPythonHandler, ABC):
    def get(self):
        obj = {'key': 'value'}
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(obj))
