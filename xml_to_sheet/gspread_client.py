import logging
from functools import lru_cache

from gspread import SpreadsheetNotFound, WorksheetNotFound
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import settings

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']


@lru_cache(maxsize=1)
def get_gspread_client():
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(
        settings.GOOGLE_SERVICE_ACCOUNT_CREDENTIAL_JSON,
        scope,
    )

    return gspread.authorize(credentials)


@lru_cache(maxsize=1)
def get_sheet(attempt_to_create=True):
    try:
        spreadsheet = get_gspread_client().open(settings.GOOGLE_SHEET_NAME)
    except SpreadsheetNotFound as e:
        if attempt_to_create:
            spreadsheet = get_gspread_client().create(settings.GOOGLE_SHEET_NAME)
        else:
            raise e

    logging.info('Google Sheet URL: https://docs.google.com/spreadsheets/d/{}'.format(spreadsheet.id))
    try:
        sheet = spreadsheet.worksheet(settings.GOOGLE_WORKSHEET_NAME)
    except WorksheetNotFound as e:
        if attempt_to_create:
            spreadsheet.add_worksheet(settings.GOOGLE_WORKSHEET_NAME)
        else:
            raise e

    return sheet
