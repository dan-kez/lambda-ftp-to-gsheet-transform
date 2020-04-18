from typing import Set
from unittest.mock import patch

import pytest

from functions.custom_lambda_exceptions import NoFilesToProcess
from services.editrade_file_service import EditradeFileService


def mock_maker_has_ftp_path_been_processed(past_files_processed: Set[str]):
    """
    Curried function to mock checking the DB.

    :param past_files_processed: strings representing files in the DB
    :return: function that checks if the first arg is in past_files_processed
    """
    return lambda ftp_path: ftp_path in past_files_processed


@patch("utils.ftp_connection.get_all_files_recursively")
@patch.object(
    EditradeFileService,
    "_has_ftp_path_been_processed",
    mock_maker_has_ftp_path_been_processed(set()),
)
def test_handle_no_files_to_filter(mock_get_files):
    from functions.determine_files_to_parse import handle

    return_set = {"file1", "file2"}
    mock_get_files.return_value = return_set
    assert handle().sort() == list(return_set).sort()


@patch("utils.ftp_connection.get_all_files_recursively")
@patch.object(
    EditradeFileService,
    "_has_ftp_path_been_processed",
    mock_maker_has_ftp_path_been_processed({"file1", "file3"}),
)
def test_handle_with_filtered_files(mock_get_files):
    from functions.determine_files_to_parse import handle

    return_set = {"file1", "file2"}
    mock_get_files.return_value = return_set
    assert handle() == ["file2"]


@patch("utils.ftp_connection.get_all_files_recursively")
@patch.object(
    EditradeFileService,
    "_has_ftp_path_been_processed",
    mock_maker_has_ftp_path_been_processed({"file1", "file2"}),
)
def test_raises_no_files_to_parse_when_appropriate(mock_get_files):
    from functions.determine_files_to_parse import handle

    return_set = {"file1", "file2"}
    mock_get_files.return_value = return_set
    with pytest.raises(NoFilesToProcess):
        handle()

    assert True


@patch.object(
    EditradeFileService,
    "_has_ftp_path_been_processed",
    mock_maker_has_ftp_path_been_processed(set()),
)
def test_handle_with_only_ftp_stub():
    from functions.determine_files_to_parse import handle

    # From the global ftp stub
    return_set = handle()
    assert len(return_set) != 0
