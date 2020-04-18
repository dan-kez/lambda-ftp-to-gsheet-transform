from pynamodb.attributes import UnicodeAttribute, UTCDateTimeAttribute, JSONAttribute
from pynamodb.indexes import LocalSecondaryIndex, KeysOnlyProjection
from pynamodb.models import Model

import settings
from models.model_mixins import CreatedTimeModelMixin, UpdateTimeModelMixin
from utils.classproperty import classproperty


class MergedFileByUpdateTime(LocalSecondaryIndex):
    class Meta:
        projection = KeysOnlyProjection()

    account_id = UnicodeAttribute(hash_key=True)
    updated_time = UTCDateTimeAttribute(range_key=True)


class EditradeMergedFile(CreatedTimeModelMixin, UpdateTimeModelMixin, Model):
    """
    The "final" merged set of file diffs. This is what we'll export
    """

    class Meta:
        # We make this a function to enable the table_name to be mockable during integration tests
        @classproperty
        def table_name(cls):
            return f"{settings.DYNAMO_TABLE_PREFIX}editrade_merged_file"

        host = settings.DYNAMO_HOST

        # Specifies the write capacity
        write_capacity_units = 1
        # Specifies the read capacity
        read_capacity_units = 1

    account_id = UnicodeAttribute(hash_key=True)
    file_id = UnicodeAttribute(range_key=True)

    # Merged set of parsed data
    parsed_data = JSONAttribute(null=False)

    merged_file_by_update_time = MergedFileByUpdateTime()
