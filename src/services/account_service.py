from functools import cached_property
from typing import List

from models.account import Account
from services.google_sheet_service import GoogleSheetService


class AccountService(object):
    """
    Get all accounts
    """

    @cached_property
    def google_sheet_service(self):
        return GoogleSheetService()

    @staticmethod
    def get_accounts() -> List[Account]:
        return list(Account.scan())

    def create_account(self, account_id: str) -> Account:
        account = Account(account_id)
        account.save()
        self.google_sheet_service.get_or_create_spreadsheet(account_id)
        return account
