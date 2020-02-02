import logging

import paramiko


def open_ftp_connection(ftp_host, ftp_port, ftp_username, ftp_password):
    """
    Opens ftp connection and returns connection object
    """
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    try:
        transport = paramiko.Transport(ftp_host, ftp_port)
    except Exception as e:
        logging.warning('conn_error')
        raise e

    try:
        transport.connect(username=ftp_username, password=ftp_password)
        ftp_connection = paramiko.SFTPClient.from_transport(transport)
    except Exception as identifier:
        logging.warning('auth error')
        raise identifier

    return ftp_connection
