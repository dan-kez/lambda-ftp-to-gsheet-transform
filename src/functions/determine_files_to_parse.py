import settings
from functions.custom_lambda_exceptions import NoFilesToProcess
from services.editrade_file_service import EditradeFileService
from utils.ftp_connection import open_ftp_connection, get_all_files_recursively


def handle():
    ftp_connection = open_ftp_connection(
        settings.FTP_HOST,
        settings.FTP_PORT,
        settings.EDITRADE_FTP_USERNAME,
        settings.EDITRADE_FTP_PASSWORD,
    )

    paths_to_consider = get_all_files_recursively(
        ftp_connection, root_path=settings.FTP_ROOT_DIR
    )
    paths_to_download = EditradeFileService.filter_known_files_from_ftp_path(
        paths_to_consider
    )

    # Circumvent subsequent executions if there are no paths to parse / download
    if len(paths_to_download) == 0:
        raise NoFilesToProcess()

    # Limit this to get around step function limitations
    return list(paths_to_download)[:100]
