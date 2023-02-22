""" Functions for establishing a connection with daybookd.
"""

import xmlrpc.client


def open(hostname, port):
    """ Create a client connection to a daybookd.

    Args:
        hostname: hostname of server.
        port: port on which server is listening.

    Returns:
        An xmlrpc client which can be used to invoke the server's methods.

    Raises:
        ConnectionRefusedError: If the server isn't up.
    """

    url = 'http://{}:{}'.format(hostname, port)

    try:
        server = xmlrpc.client.ServerProxy(url, allow_none=True)
        server.ping()
    except ConnectionRefusedError:
        raise ConnectionRefusedError('No daybookd listening at {}'.format(url))

    return server
