from .application import SimpleApp1


def _jupyter_server_extension_paths():
    return [{
        'module': 'pretty-python-server.application',
        'app': SimpleApp1
    }]
