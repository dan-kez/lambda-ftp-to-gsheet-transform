from datetime import datetime
from unittest.mock import patch
from uuid import uuid1

import pytest
from dateutil.tz import tzutc

from models.editrade_file_update import EditradeFileUpdate

sentinel_datetime = datetime(1901, 2, 1, tzinfo=tzutc())


@pytest.mark.parametrize("input_data", [{}, {"asd": "asd"}])
def test_set_all_fields_for_processed_data(input_data):
    with patch("models.editrade_file_update.datetime") as datetime_mock:
        datetime_mock.utcnow.return_value = sentinel_datetime

        editrade_file_update = EditradeFileUpdate(
            file_uuid="uuid",
            editrade_upload_date=datetime.utcnow(),
            account_id="123",
            file_id="2223",
            s3_xml_path="BS FILE PATH",
        )

        editrade_file_update.set_parsed_data(input_data)
        assert editrade_file_update.parsed_data == input_data
        assert editrade_file_update.parsed_time == sentinel_datetime
        assert editrade_file_update.needs_processing is False


@pytest.mark.parametrize(
    "input_data,thrown_error_message",
    [
        [{}, ""],
        [{"asd": "asd"}, ""],
        [{"key1": 12, "key2": "string val"}, "All values must be strings"],
        [{12: "foo", "key2": "string val"}, "All keys must be strings"],
    ],
    ids=["No data", "Basic dict", "Dict with invalid value", "Dict with invalid key"],
)
@pytest.mark.integration
def test_set_all_fields_for_processed_data_already_saved(
    input_data, thrown_error_message, fixture_model_management
):
    with patch("models.editrade_file_update.datetime") as datetime_mock:
        datetime_mock.utcnow.return_value = sentinel_datetime
        file_uuid = str(uuid1())

        editrade_file_update = EditradeFileUpdate(
            file_uuid=file_uuid,
            editrade_upload_date=datetime.utcnow(),
            account_id="123",
            file_id="2223",
            s3_xml_path="BS FILE PATH",
        )
        # Ensure Defaults are correct
        assert editrade_file_update.parsed_data is None
        assert editrade_file_update.parsed_time is None
        assert editrade_file_update.needs_processing is True
        editrade_file_update.save()

        retrieved_record = EditradeFileUpdate.get(file_uuid)
        # Ensure retrieved are correct
        assert retrieved_record.parsed_data is None
        assert retrieved_record.parsed_time is None
        assert retrieved_record.needs_processing is True

        if thrown_error_message:
            with pytest.raises(AssertionError, match=thrown_error_message):
                retrieved_record.set_parsed_data(input_data)
            retrieved_record.delete()
            return
        else:
            retrieved_record.set_parsed_data(input_data)

        # Ensure set, but pre save values are correct
        assert retrieved_record.parsed_data == input_data
        assert retrieved_record.parsed_time == sentinel_datetime
        assert retrieved_record.needs_processing is False
        retrieved_record.save()

        # Ensure set, but post save values are correct
        assert retrieved_record.parsed_data == input_data
        assert retrieved_record.parsed_time == sentinel_datetime
        assert retrieved_record.needs_processing is False

        retrieved_record_2 = EditradeFileUpdate.get(file_uuid)
        # Ensure set, post save, and post fetch to new object are correct
        assert retrieved_record_2.parsed_data == input_data
        assert retrieved_record_2.parsed_time == sentinel_datetime
        assert retrieved_record_2.needs_processing is False

        # Delete to mitigate collision
        retrieved_record_2.delete()
