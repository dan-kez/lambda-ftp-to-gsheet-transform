from pynamodb.attributes import UnicodeAttribute
from pynamodb.models import Model

import settings
from models.model_mixins import CreatedTimeModelMixin, UpdateTimeModelMixin
from utils.classproperty import classproperty


class Account(UpdateTimeModelMixin, CreatedTimeModelMixin, Model):
    """
    A set of account ids
    """

    class Meta:
        # We make this a function to enable the table_name to be mockable during integration tests
        @classproperty
        def table_name(cls):
            return f"{settings.DYNAMO_TABLE_PREFIX}account"

        host = settings.DYNAMO_HOST

        # Specifies the write capacity
        write_capacity_units = 1
        # Specifies the read capacity
        read_capacity_units = 1

    # editrade account_id
    account_id = UnicodeAttribute(hash_key=True)
