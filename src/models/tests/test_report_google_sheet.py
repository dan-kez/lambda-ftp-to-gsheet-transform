import pytest

from models.report_google_sheet import ReportGoogleSheet


@pytest.mark.integration
def test_raises_if_google_spreadsheet_id_is_not_provided(fixture_model_management):
    report_google_sheet = ReportGoogleSheet(account_id="123")
    with pytest.raises(
        ValueError, match="Attribute 'google_spreadsheet_id' cannot be None"
    ):
        report_google_sheet.save()


@pytest.mark.integration
def test_exists_check_works(fixture_model_management):
    assert ReportGoogleSheet.record_exists("asd") is False
    report_google_sheet = ReportGoogleSheet(
        account_id="123", google_spreadsheet_id="foo"
    )
    report_google_sheet.save()
    assert ReportGoogleSheet.record_exists("123") is True
