from datetime import datetime
from typing import Dict

from pynamodb.attributes import (
    UnicodeAttribute,
    NumberAttribute,
    JSONAttribute,
    UTCDateTimeAttribute,
)
from pynamodb.indexes import (
    GlobalSecondaryIndex,
    KeysOnlyProjection,
    IncludeProjection,
)
from pynamodb.models import Model

import settings
from models.custom_attributes import BooleanAsNumberAttribute
from models.model_mixins import CreatedTimeModelMixin, UpdateTimeModelMixin
from utils.classproperty import classproperty


class FilesToProcessIndex(GlobalSecondaryIndex):
    """
    A look up index to quickly find all files that need to be processed
    """

    class Meta:
        read_capacity_units = 1
        write_capacity_units = 1
        projection = KeysOnlyProjection()

    needs_processing = BooleanAsNumberAttribute(hash_key=True)
    file_uuid = NumberAttribute()


class FileDiffsByAccountIndex(GlobalSecondaryIndex):
    """
    A look up index to query file records by upload date
    """

    class Meta:
        read_capacity_units = 1
        write_capacity_units = 1
        projection = IncludeProjection(non_attr_keys=["file_id", "file_uuid"])

    account_id = UnicodeAttribute(hash_key=True)
    editrade_upload_date = UTCDateTimeAttribute(range_key=True)


class AccountIDByParseTime(GlobalSecondaryIndex):
    """
    A look up index to determine the processed time per account
    """

    class Meta:
        read_capacity_units = 1
        write_capacity_units = 1
        projection = KeysOnlyProjection()

    account_id = UnicodeAttribute(hash_key=True)
    parsed_time = UTCDateTimeAttribute(range_key=True)


class FileDiffsByFileIDIndex(GlobalSecondaryIndex):
    """
    A look up index to quickly merge by file id for the given account
    """

    class Meta:
        read_capacity_units = 1
        write_capacity_units = 1
        projection = IncludeProjection(
            non_attr_keys=["account_id", "parsed_data", "file_uuid"]
        )

    file_id = UnicodeAttribute(hash_key=True)
    editrade_upload_date = UTCDateTimeAttribute(range_key=True)


class EditradeFileUpdate(CreatedTimeModelMixin, UpdateTimeModelMixin, Model):
    """
    A source of editrade file diffs
    """

    class Meta:
        # We make this a function to enable the table_name to be mockable during integration tests
        @classproperty
        def table_name(cls):
            return f"{settings.DYNAMO_TABLE_PREFIX}editrade_file_update"

        host = settings.DYNAMO_HOST

        # Specifies the write capacity
        write_capacity_units = 1
        # Specifies the read capacity
        read_capacity_units = 1

    files_to_process_index = FilesToProcessIndex()
    file_diffs_by_file_id_index = FileDiffsByFileIDIndex()
    file_diffs_by_account_index = FileDiffsByAccountIndex()
    account_id_by_parse_time_index = AccountIDByParseTime()

    # editrade provided file uuid
    file_uuid = UnicodeAttribute(hash_key=True)

    # Parsed from the editrade file name
    editrade_upload_date = UTCDateTimeAttribute(null=False)

    # Account and file id for secondary indices
    account_id = UnicodeAttribute(null=False)
    file_id = UnicodeAttribute(null=False)

    # Location of XML
    s3_xml_path = UnicodeAttribute(null=False)

    # Parsed data for the given XML file
    parsed_data = JSONAttribute(null=True)

    # Time when last parsed
    parsed_time = UTCDateTimeAttribute(null=True)

    # For use in the GSI
    needs_processing = BooleanAsNumberAttribute(default_for_new=True)

    def set_parsed_data(self, parsed_data: Dict[str, str]) -> None:
        """
        Sets all necessary properties when setting processed data for the file update

        :param parsed_data:
        :return: not meaningful
        """
        for key, value in parsed_data.items():
            assert type(key) == str, "All keys must be strings"
            assert type(value) == str, "All values must be strings"

        self.parsed_data = parsed_data
        self.parsed_time = datetime.utcnow()
        self.needs_processing = False

    @classmethod
    def record_exists(cls, hash_key) -> bool:
        try:
            cls.query(hash_key).next()
        except StopIteration:
            return False

        return True
