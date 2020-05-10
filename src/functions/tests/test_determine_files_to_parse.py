from datetime import datetime
from typing import Set
from unittest.mock import patch

import pytest
from dateutil.tz import tzutc

from functions.custom_lambda_exceptions import NoFilesToProcess
from models.editrade_file_update import EditradeFileUpdate
from services.editrade_ftp_file_parser import EditradeFTPFileParser

today_string = datetime.now(tzutc()).strftime(EditradeFTPFileParser.TIME_FORMAT)
file_1_uuid = "A5058E79-2160-4F4E-8E3D-9F406D918449"
file_1 = f"/Usr/macship/EDITRADEOUT/001940/EntryExtract-141888-D37{{{today_string}}}{{{file_1_uuid}}}.xml"
file_2_uuid = "A5022E79-2160-4F4E-8E3D-9F406D22449"
file_2 = f"/Usr/macship/EDITRADEOUT/001940/EntryExtract-141888-D37{{{today_string}}}{{{file_2_uuid}}}.xml"
file_3_uuid = "A5022E79-2160-4F4E-8E3D-9F402222222"
file_3 = f"/Usr/macship/EDITRADEOUT/001940/EntryExtract-141888-D37{{{today_string}}}{{{file_3_uuid}}}.xml"


def mock_maker_batch_get(past_files_processed: Set[str]):
    """
    Curried function to mock checking the DB.

    :param past_files_processed: strings representing files in the DB
    :return: function that checks if the first arg is in past_files_processed
    """

    def inner_batch_get_mock(uuid_ids_to_look_up, attributes_to_get):
        past_processed_uuids = past_files_processed.intersection(
            set(uuid_ids_to_look_up)
        )
        return [
            EditradeFileUpdate(file_uuid=file_uuid)
            for file_uuid in past_processed_uuids
        ]

    return inner_batch_get_mock


@patch("utils.ftp_connection.get_all_files_recursively")
@patch.object(
    EditradeFileUpdate, "batch_get", mock_maker_batch_get(set()),
)
def test_handle_no_files_to_filter(mock_get_files):
    from functions.determine_files_to_parse import handle

    return_set = {file_1, file_2}
    mock_get_files.return_value = return_set
    assert handle().sort() == list(return_set).sort()


@patch("utils.ftp_connection.get_all_files_recursively")
@patch.object(
    EditradeFileUpdate, "batch_get", mock_maker_batch_get({file_1_uuid, file_3_uuid}),
)
def test_handle_with_filtered_files(mock_get_files):
    from functions.determine_files_to_parse import handle

    return_set = {file_1, file_2}
    mock_get_files.return_value = return_set
    assert handle() == [file_2]


@patch("utils.ftp_connection.get_all_files_recursively")
@patch.object(
    EditradeFileUpdate, "batch_get", mock_maker_batch_get({file_1_uuid, file_2_uuid}),
)
def test_raises_no_files_to_parse_when_appropriate(mock_get_files):
    from functions.determine_files_to_parse import handle

    return_set = {file_1, file_2}
    mock_get_files.return_value = return_set
    with pytest.raises(NoFilesToProcess):
        handle()

    assert True


@patch.object(
    EditradeFileUpdate, "batch_get", mock_maker_batch_get(set()),
)
def test_handle_with_only_ftp_stub():
    from functions.determine_files_to_parse import handle

    # From the global ftp stub
    return_set = handle()
    assert len(return_set) != 0
