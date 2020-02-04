import bisect
import logging
import re
import time
from collections import defaultdict
from datetime import datetime
from distutils.util import strtobool
from urllib.parse import unquote

import settings
from ftp_to_s3 import transfer_all_editrade_files_to_s3
from ftp_to_s3.ftp_file_cleanup import remove_old_files_from_ftp
from utils import get_matching_s3_keys
from xml_to_sheet.send_to_google_sheets import parse_s3_xml_file_to_sheet

logging.getLogger().setLevel(logging.INFO)


def handler_transfer_editrade_files_to_s3(event, context):
    days_back = int(event.get('days_back', 1))
    transfer_all_editrade_files_to_s3(days_back=days_back)


def handler_parse_s3_xml_file_to_sheet(event, context):
    for record in event.get('Records'):
        uploaded_s3_file_key = unquote(record.get('s3').get('object').get('key'))
        logging.info('Processing for s3 file key: {}'.format(uploaded_s3_file_key))
        parse_s3_xml_file_to_sheet(uploaded_s3_file_key)


def handler_bulk_parse_xml_files(event, context):
    days_back = int(event.get('days_back', 1))

    # File number to list of tuples where the time of upload is the first index and the s3 key is the second index.
    # We need to replay the files in the correct order so that the resulting data in the spreadsheet is correct as
    # some fields are overwritten between files.
    replay_mapping = defaultdict(list)

    # TODO: Will likely get inefficient as the bucket grows. Potentially add an early bailout,
    for s3_key in get_matching_s3_keys(settings.S3_BUCKET_NAME, prefix=settings.S3_ROOT_DIR, days_back=days_back):

        matches = re.search(r'EntryExtract-(\d+)-\w+\{([^}]+)\}', s3_key)

        # We can't just rely on file ordering in s3 as we may need to backfill the s3 bucket.
        # Instead parse the file name.
        if matches:
            file_number = matches.group(1)
            datetime_string = matches.group(2)
            file_created_time = datetime.strptime(datetime_string, '%Y-%m-%d-%H%M%S')
            bisect.insort(replay_mapping[file_number], (file_created_time.timestamp(), s3_key,))
        else:
            logging.warning('{} | Error: could not match expected file pattern for s3 path'.format(s3_key))

    for file_number, file_tuple_list in replay_mapping.items():
        for time_ftp_file_created, s3_key in file_tuple_list:
            logging.info('Processing for s3 file key: {}'.format(s3_key))

            parse_s3_xml_file_to_sheet(s3_key)
            time.sleep(1)  # Cheap To help mitigate rate limits.


def handler_delete_old_files(event, context):
    days_back = int(event.get('days_back', 30))
    dry_run = event.get('dry_run', True)
    if not isinstance(dry_run, bool):
        raise ValueError('dry_run must either be a boolean input. Got {}'.format(dry_run))

    remove_old_files_from_ftp(days_back=days_back, dry_run=dry_run)

