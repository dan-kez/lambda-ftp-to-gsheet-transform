import os
import re
from datetime import datetime

from dateutil.tz import tzutc

import settings
from functions.custom_lambda_exceptions import InvalidFileName
from models.editrade_file_update import EditradeFileUpdate


class EditradeFTPFileParser(object):
    FTP_PATH_REGEX = re.compile(
        r".*/(\d+)/(EntryExtract-(\d+)-\w+{([\d-]+)}{([\w-]+)}.*\.xml)$"
    )
    S3_ROOT_DIR = settings.S3_ROOT_DIR
    TIME_FORMAT = "%Y-%m-%d-%H%M%S"

    def __init__(self, ftp_path):
        self.ftp_path = ftp_path

        matches = self.FTP_PATH_REGEX.match(self.ftp_path)
        if not matches:
            raise InvalidFileName("ftp_path must match FTP_PATH_REGEX")
        account_id, file_name, file_id, _raw_date, file_uuid = matches.groups()

        self.account_id = account_id
        self.file_name = file_name
        self.file_id = file_id
        self._raw_date = _raw_date
        self.file_uuid = file_uuid

    @property
    def s3_path(self):
        return os.path.join(self.S3_ROOT_DIR, self.account_id, self.file_name)

    @property
    def datetime(self):
        return datetime.strptime(self._raw_date, self.TIME_FORMAT).replace(
            tzinfo=tzutc()
        )

    def to_editrade_file_update(self):
        return EditradeFileUpdate(
            file_uuid=self.file_uuid,
            editrade_upload_date=self.datetime,
            account_id=self.account_id,
            file_id=self.file_id,
            s3_xml_path=self.s3_path,
        )

    def __str__(self):
        return f"EditradeFile: Account {self.account_id} | FileID {self.file_id} | FileName {self.file_name}"
