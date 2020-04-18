import pytest

from functions.custom_lambda_exceptions import InvalidFileName
from models.editrade_file_update import EditradeFileUpdate
from services.editrade_ftp_file_parser import EditradeFTPFileParser
from settings import S3_ROOT_DIR


@pytest.mark.parametrize(
    "test_input,expected",
    [
        [
            "/Usr/macship/EDITRADEOUT/002113/EntryExtract-141717-D37{2020-03-18-130639}{02053D1D-262E-43B7-9D77-3B2C9B58DB64}.xml",
            [
                "002113",
                "141717",
                "2020-03-18-130639",
                "02053D1D-262E-43B7-9D77-3B2C9B58DB64",
                "EntryExtract-141717-D37{2020-03-18-130639}{02053D1D-262E-43B7-9D77-3B2C9B58DB64}.xml",
                f"{S3_ROOT_DIR}002113/EntryExtract-141717-D37{{2020-03-18-130639}}{{02053D1D-262E-43B7-9D77-3B2C9B58DB64}}.xml",
                1584536799.0,
            ],
        ],
        [
            "/Usr/macship/EDITRADEOUT/001940/EntryExtract-141856-D37{2020-04-04-094100}{29D81A29-34FB-4993-AE12-8F19986EAA13}.xml",
            [
                "001940",
                "141856",
                "2020-04-04-094100",
                "29D81A29-34FB-4993-AE12-8F19986EAA13",
                "EntryExtract-141856-D37{2020-04-04-094100}{29D81A29-34FB-4993-AE12-8F19986EAA13}.xml",
                f"{S3_ROOT_DIR}001940/EntryExtract-141856-D37{{2020-04-04-094100}}{{29D81A29-34FB-4993-AE12-8F19986EAA13}}.xml",
                1585993260.0,
            ],
        ],
        # Error thrown case
        ["BS INPUT", []],
    ],
)
def test_eval(test_input, expected):
    if not expected:
        with pytest.raises(InvalidFileName, match="ftp_path must match FTP_PATH_REGEX"):
            EditradeFTPFileParser(test_input)
    else:
        editrade_file = EditradeFTPFileParser(test_input)
        (
            account_id,
            file_id,
            raw_date,
            file_uuid,
            file_name,
            s3_path,
            unix_timestamp,
        ) = expected
        assert editrade_file.account_id == account_id
        assert editrade_file.file_id == file_id
        assert editrade_file._raw_date == raw_date
        assert editrade_file.file_uuid == file_uuid
        assert editrade_file.file_name == file_name
        assert editrade_file.ftp_path == test_input
        assert editrade_file.s3_path == s3_path
        assert editrade_file.datetime.timestamp() == unix_timestamp


@pytest.mark.integration
def test_to_dynamodb_model(fixture_model_management):
    ftp_path = "/Usr/macship/EDITRADEOUT/001940/EntryExtract-141856-D37{2020-04-04-094100}{29D81A29-34FB-4993-AE12-8F19986EAA13}.xml"
    (account_id, file_id, raw_date, file_uuid, file_name, s3_path, unix_timestamp) = [
        "001940",
        "141856",
        "2020-04-04-094100",
        "29D81A29-34FB-4993-AE12-8F19986EAA13",
        "EntryExtract-141856-D37{2020-04-04-094100}{29D81A29-34FB-4993-AE12-8F19986EAA13}.xml",
        f"{S3_ROOT_DIR}001940/EntryExtract-141856-D37{{2020-04-04-094100}}{{29D81A29-34FB-4993-AE12-8F19986EAA13}}.xml",
        1585993260.0,
    ]
    editrade_ftp_file_parser = EditradeFTPFileParser(ftp_path)
    editrade_file_update = editrade_ftp_file_parser.to_editrade_file_update()

    # Should save successfully
    editrade_file_update.save()

    file_from_db = EditradeFileUpdate.get(file_uuid)
    assert file_from_db.needs_processing  # Defaults to true
    assert file_from_db.account_id == account_id
    assert file_from_db.file_id == file_id
    assert file_from_db.file_uuid == file_uuid
    assert file_from_db.parsed_data is None
    assert file_from_db.parsed_time is None
    assert file_from_db.s3_xml_path == s3_path
    assert file_from_db.editrade_upload_date.timestamp() == unix_timestamp
