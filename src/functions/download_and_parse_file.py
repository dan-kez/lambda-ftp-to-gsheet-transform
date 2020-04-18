from services.editrade_file_service import EditradeFileService


def handle(ftp_file_path):
    """
    This will download the given file, upload it to s3, parse its values into the db and merge all diffs
    into the merged table.

    We do this synchronously, but have data fields to mark if something is processed to be able to recover
    from errors.

    :param ftp_file_path:
    :return: Not meaningful
    """
    EditradeFileService().create_file_update_from_ftp_path(ftp_file_path)
