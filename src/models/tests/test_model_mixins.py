from datetime import datetime
from unittest.mock import patch

import pytest
from dateutil.tz import tzutc
from pynamodb.attributes import NumberAttribute
from pynamodb.models import Model

import settings
from models.model_mixins import CreatedTimeModelMixin, UpdateTimeModelMixin
from utils.classproperty import classproperty

sentinel_datetime = datetime(1901, 2, 1, tzinfo=tzutc())


@patch("models.model_mixins.datetime")
def test_created_datetime_is_set(mock_datetime):
    class TestModel(Model, CreatedTimeModelMixin):
        class Meta:
            table_name = "Does not matter"
            host = "fake"

    mock_datetime.utcnow.return_value = sentinel_datetime
    test_model = TestModel()
    assert test_model.created_time == sentinel_datetime


@patch("models.model_mixins.datetime")
@pytest.mark.integration
def test_updated_time_is_reset_on_save(mock_datetime, fixture_model_management):
    class TestModel(UpdateTimeModelMixin, Model):
        class Meta:
            @classproperty
            def table_name(self):
                return f"{settings.DYNAMO_TABLE_PREFIX}Does_not_matter"

            host = settings.DYNAMO_HOST
            write_capacity_units = 1
            read_capacity_units = 1

        id = NumberAttribute(hash_key=True)
        other_prop = NumberAttribute()

    TestModel.create_table(wait=True)

    mock_datetime.utcnow.return_value = sentinel_datetime
    test_model = TestModel(1, other_prop=1)
    assert test_model.updated_time == sentinel_datetime
    assert test_model.other_prop == 1
    test_model.save()

    sentinel_datetime_2 = datetime(2001, 2, 1, tzinfo=tzutc())
    mock_datetime.utcnow.return_value = sentinel_datetime_2

    test_model_2 = TestModel(1, other_prop=2)
    assert test_model_2.updated_time == sentinel_datetime_2
    assert test_model_2.other_prop == 2
    test_model_2.save()
    assert test_model_2.updated_time == sentinel_datetime_2

    sentinel_datetime_3 = datetime(2222, 2, 1, tzinfo=tzutc())
    mock_datetime.utcnow.return_value = sentinel_datetime_3

    queried_test_model = TestModel.get(1)
    # Despite mock being in future this should point to the stored value
    assert queried_test_model.updated_time == sentinel_datetime_2
    assert queried_test_model.other_prop == 2

    queried_test_model.other_prop = 3
    queried_test_model.save()

    assert queried_test_model.updated_time == sentinel_datetime_3
    TestModel.delete_table()
