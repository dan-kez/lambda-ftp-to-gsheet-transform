from functions import (
    determine_files_to_parse,
    download_and_parse_file,
    update_google_sheets,
)


def checknewfiles(event, context):
    return determine_files_to_parse.handle()


def downloadandprocesseditradefile(ftp_file_path, context):
    """

    :param event: ftp file path to process
    :param context:
    :return: None
    """
    download_and_parse_file.handle(ftp_file_path)
    return None


def updategooglesheets(event, context):
    """
    Cronned function responsible for updating the google sheet representation of an account's data
    """

    update_google_sheets.handle(
        days=event.get("days", 0),
        hours=event.get("hours", 0),
        minutes=event.get("minutes", 0),
    )
    return None
