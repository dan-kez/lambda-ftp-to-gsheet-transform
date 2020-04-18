from datetime import timedelta

from services.account_service import AccountService
from services.editrade_file_service import EditradeFileService
from services.google_sheet_service import GoogleSheetService


def handle(days: float = 0, hours: float = 1, minutes: float = 0):
    """
    Cronned function responsible for updating the google sheet representation of an account's data

    :param days:
    :param hours:
    :param minutes:
    :return: Not meaningful
    """
    google_sheet_service = GoogleSheetService()
    input_timedelta = timedelta(days=days, hours=hours, minutes=minutes)
    # Get all account ids
    accounts = AccountService.get_accounts()

    for account in accounts:
        account_id = account.account_id
        # For each account id check if the result is within the input time range
        has_updates_in_requested_timedelta = EditradeFileService.is_last_parsed_time_for_account_within_timedelta(
            account_id, input_timedelta=input_timedelta,
        )
        # If it is then run create csv for account
        if has_updates_in_requested_timedelta:
            csv_result = EditradeFileService.create_all_file_report_for_account_id(
                account_id
            )
            # Pass CSV Data to Google Sheets, consider saving diffs in s3 for audit
            google_sheet_service.update_sheet_for_account_id(account_id, csv_result)
