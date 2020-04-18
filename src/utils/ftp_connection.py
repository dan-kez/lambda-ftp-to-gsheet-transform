import logging
import os
from stat import S_ISDIR, S_ISREG

import paramiko

_ftp_connection = None
_transport = None
# For use in mocks during testing
allow_connection_reuse = True


def close_ftp_connection():
    global _transport
    global _ftp_connection

    if _transport:
        _transport.close()
        _transport = None
    if _ftp_connection:
        _ftp_connection.close()
        _ftp_connection = None


def open_ftp_connection(ftp_host, ftp_port, ftp_username, ftp_password):
    """
    Opens ftp connection and returns connection object
    """
    global _transport
    global _ftp_connection

    assert _ftp_connection is None or (
        _ftp_connection is not None and allow_connection_reuse
    )
    if _ftp_connection and allow_connection_reuse:
        return _ftp_connection

    client = paramiko.SSHClient()
    client.load_system_host_keys()

    try:
        _transport = paramiko.Transport((ftp_host, ftp_port))
    except Exception as e:
        logging.warning("conn_error")
        raise e

    try:
        _transport.connect(username=ftp_username, password=ftp_password)
        _ftp_connection = paramiko.SFTPClient.from_transport(_transport)
    except Exception as identifier:
        logging.warning("auth error")
        raise identifier

    return _ftp_connection


def get_all_files_recursively(ftp_connection, root_path="/"):
    output_files = set()
    for file in ftp_connection.listdir_attr(root_path):
        mode = file.st_mode
        if S_ISDIR(mode):
            output_files |= get_all_files_recursively(
                ftp_connection, root_path=os.path.join(root_path, file.filename)
            )
        elif S_ISREG(mode):
            output_files.add(os.path.join(root_path, file.filename))
    return output_files
