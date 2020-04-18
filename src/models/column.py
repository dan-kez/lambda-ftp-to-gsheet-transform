from ctypes import Array
from typing import Type

from pynamodb.attributes import (
    UnicodeAttribute,
    NumberAttribute,
    BooleanAttribute,
)
from pynamodb.models import Model

import settings
from models.model_mixins import CreatedTimeModelMixin, UpdateTimeModelMixin
from utils.classproperty import classproperty


class AccountColumn(UpdateTimeModelMixin, CreatedTimeModelMixin, Model):
    """
    A mapping of columns for a given account id
    """

    class Meta:
        # We make this a function to enable the table_name to be mockable during integration tests
        @classproperty
        def table_name(cls):
            return f"{settings.DYNAMO_TABLE_PREFIX}account-column"

        host = settings.DYNAMO_HOST

        # Specifies the write capacity
        write_capacity_units = 1
        # Specifies the read capacity
        read_capacity_units = 1

    # editrade account_id
    account_id = UnicodeAttribute(hash_key=True)

    # User facing column name
    column_name = UnicodeAttribute(range_key=True)

    # xpath lookup in to hydrate value from XML document
    xpath_query = UnicodeAttribute()

    # HACK: For some accounts we want multiple roles per file processed (e.g. by item no)
    # to support this late feature request we'll add a relative_to_xpath that we will look up
    # before processing start all lookups from that node. This enables some `xpath_query` entries
    # to use relative xpath syntax such at `./node_name`
    # There should only be one relative_to_xpath per_account at present. This isn't enforced by the schema
    # but I plan to migrate from dynamodb soon anyways given it's cost/ query limitations.
    relative_to_xpath = UnicodeAttribute(default="/")

    # If true, transform multiple results to a CSV
    has_multiple = BooleanAttribute(default=False)

    # For manual non alphabetic ordering per column_name
    order = NumberAttribute(default=0)

    @classmethod
    def get_columns_for_account_id(cls, account_id):
        # This is getting all of the columns ordered by name by default
        # We could make this more efficient with some other index but the number
        # of columns per account is very small at present.
        account_columns = list(cls.query(account_id))

        return sorted(account_columns, key=lambda column: column.order)
