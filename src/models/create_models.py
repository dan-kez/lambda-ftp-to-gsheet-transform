from models.account import Account
from models.column import AccountColumn
from models.editrade_file_update import EditradeFileUpdate
from models.editrade_merged_file import EditradeMergedFile
from models.report_google_sheet import ReportGoogleSheet


def create_models(wait=True):
    Account.create_table(wait=wait)
    AccountColumn.create_table(wait=wait)
    EditradeFileUpdate.create_table(wait=wait)
    EditradeMergedFile.create_table(wait=wait)
    ReportGoogleSheet.create_table(wait=wait)


def delete_models():
    AccountColumn.delete_table()
    EditradeFileUpdate.delete_table()
    EditradeMergedFile.delete_table()
    ReportGoogleSheet.delete_table()
