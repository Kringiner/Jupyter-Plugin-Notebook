from .handler import PrettyPythonHandler
from notebook.utils import url_path_join

EXTENSION_API_ROUTE = '/pretty-python-server/pretty-code'


def load_jupyter_server_extension(nb_server_app):
    web_app = nb_server_app.web_app
    host_pattern = '.*$'
    route_pattern = url_path_join(web_app.settings['base_url'], EXTENSION_API_ROUTE)
    web_app.add_handlers(host_pattern, [(route_pattern, PrettyPythonHandler)])
