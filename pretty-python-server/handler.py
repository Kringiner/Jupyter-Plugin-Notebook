import json
from abc import ABC

from notebook.base.handlers import IPythonHandler


class PrettyPythonHandler(IPythonHandler, ABC):
    def post(self):
        obj = self.get_json_body()
        self.set_header("Content-Type", "application/json")
        self.set_status(200)
        self.write(json.dumps(obj))
