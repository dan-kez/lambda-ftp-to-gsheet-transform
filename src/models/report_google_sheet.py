from pynamodb.attributes import UnicodeAttribute
from pynamodb.models import Model

import settings
from models.model_mixins import CreatedTimeModelMixin, UpdateTimeModelMixin
from utils.classproperty import classproperty


class ReportGoogleSheet(UpdateTimeModelMixin, CreatedTimeModelMixin, Model):
    """
    A mapping of account ids to google sheets
    """

    DEFAULT_GOOGLE_WORKSHEET_NAME = "RAW_DATA_DO_NOT_EDIT"
    DEFAULT_GOOGLE_SPREADSHEET_NAME = "Editrade Sync"

    class Meta:
        # We make this a function to enable the table_name to be mockable during integration tests
        @classproperty
        def table_name(cls):
            return f"{settings.DYNAMO_TABLE_PREFIX}report-google-sheet"

        host = settings.DYNAMO_HOST

        # Specifies the write capacity
        write_capacity_units = 1
        # Specifies the read capacity
        read_capacity_units = 1

    # editrade account_id
    account_id = UnicodeAttribute(hash_key=True)

    # Google Spreadsheet key
    google_spreadsheet_id = UnicodeAttribute(null=False)

    # Google spreadsheet name
    google_spreadsheet_name = UnicodeAttribute(
        default_for_new=DEFAULT_GOOGLE_SPREADSHEET_NAME
    )

    # Google worksheet name
    google_worksheet_name = UnicodeAttribute(
        default_for_new=DEFAULT_GOOGLE_WORKSHEET_NAME
    )

    @property
    def spreadsheet_url(self):
        return f"https://docs.google.com/spreadsheets/d/{self.google_spreadsheet_id}"

    @classmethod
    def record_exists(cls, hash_key) -> bool:
        try:
            cls.query(hash_key).next()
        except StopIteration:
            return False

        return True
