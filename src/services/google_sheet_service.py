import logging
from functools import cached_property, lru_cache
from typing import List, Union, Literal

import gspread
from google.oauth2.service_account import Credentials
from gspread import WorksheetNotFound

import settings
from models.report_google_sheet import ReportGoogleSheet

scopes = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]


class GoogleSheetService(object):
    @cached_property
    def gspread_client(self):
        credentials = Credentials.from_service_account_info(
            settings.GOOGLE_SERVICE_ACCOUNT_CREDENTIAL_JSON, scopes=scopes,
        )

        return gspread.authorize(credentials)

    @lru_cache(maxsize=1)
    def get_or_create_spreadsheet(self, account_id: str):
        try:
            report_google_sheet_object = ReportGoogleSheet.get(account_id)
            spreadsheet = self.gspread_client.open_by_key(
                report_google_sheet_object.google_spreadsheet_id
            )
        except ReportGoogleSheet.DoesNotExist:
            report_google_sheet_object = ReportGoogleSheet(account_id)
            spreadsheet = self.gspread_client.create(
                report_google_sheet_object.google_spreadsheet_name
            )
            report_google_sheet_object.google_spreadsheet_id = spreadsheet.id
            report_google_sheet_object.save()

            logging.info(
                f"Created Google Sheet URL for {account_id}: {report_google_sheet_object.spreadsheet_url}"
            )
        return spreadsheet

    @lru_cache(maxsize=1)
    def get_or_create_worksheet(
        self, account_id: str,
    ):
        # TODO: We get this same object twice, consider caching it
        spreadsheet = self.get_or_create_spreadsheet(account_id)
        report_google_sheet_object = ReportGoogleSheet.get(account_id)

        try:
            worksheet = spreadsheet.worksheet(
                report_google_sheet_object.google_worksheet_name
            )
        except WorksheetNotFound as e:
            worksheet = spreadsheet.add_worksheet(
                report_google_sheet_object.google_worksheet_name, 1000, 100
            )

        return worksheet

    def update_sheet_for_account_id(self, account_id: str, csv_data: List[List[str]]):
        """
        Looks up sheet for the given account and sets the data in the google sheet. Note, this clears the sheet at the
        start of each call

        :param account_id: The account sheet to update
        :param csv_data: The csv data to include. This should include headers
        :return: not meaningful
        """
        worksheet = self.get_or_create_worksheet(account_id)
        worksheet.clear()
        worksheet.update("A:ZZZ", csv_data)

    def share_spreadsheet_with_email(
        self, account_id: str, email: str, role: Literal["reader", "writer"] = "reader"
    ):
        """
        Gives the email permissions to the sheet associated with the account_id

        :param account_id: The account sheet to update
        :param email:
        :param role:
        :return: not meaningful
        """
        spreadsheet = self.get_or_create_spreadsheet(account_id)
        spreadsheet.share(email, perm_type="user", role=role)
