from handler import downloadandprocesseditradefile, updategooglesheets
from models.create_models import create_models
from models.editrade_file_update import FilesToProcessIndex, EditradeFileUpdate
from models.report_google_sheet import ReportGoogleSheet
from services import google_sheet_service
from services.editrade_file_service import EditradeFileService
from services.google_sheet_service import GoogleSheetService

"""
Helper file to create all tables in one command
"""

if __name__ == "__main__":
    # account_id = "002113"
    account_id = "001940"
    #
    # editrade_file_service = EditradeFileService()
    # editrade_file_service.reprocess_files(account_id)

    # with EditradeFileUpdate.batch_write() as batch:
    #     for file in EditradeFileUpdate.scan():
    #         file.needs_processing = True
    #         batch.save(file)
    # editrade_file_service.merge_recent_processed_files_for_account_id(
    #     account_id, days_back=30
    # )
    # processedfiles = list(
    #     EditradeFileUpdate.scan(EditradeFileUpdate.needs_processing == True)
    # )
    # for file in processedfiles:
    #     editrade_file_service.process_by_editrade_file_update_object(file)
    # account_id = "002113"
    # downloadandprocesseditradefile(
    #     "/Usr/macship/EDITRADEOUT/002113/EntryExtract-141945-D37{2020-04-16-140437}{4150BE4E-9816-46B0-9ABC-EA03C035B429}.xml",
    #     {},
    # )
    # updategooglesheets({"hours": 1}, {})
    report = ReportGoogleSheet.get(account_id)
    sheet = GoogleSheetService().get_or_create_spreadsheet(account_id)
    sheet.share("daniel.kez@gmail.com", perm_type="user", role="writer")
    print(report.spreadsheet_url)
