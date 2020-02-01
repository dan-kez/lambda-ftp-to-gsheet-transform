from urllib.parse import unquote

import settings
from ftp_to_s3 import transfer_all_editrade_files_to_s3
from utils import get_matching_s3_keys
from xml_to_sheet import parse_s3_xml_file_to_sheet


def handler_transfer_editrade_files_to_s3(event, context):
    days_back = int(event.get('days_back', 1))
    transfer_all_editrade_files_to_s3(days_back=days_back)


def handler_parse_s3_xml_file_to_sheet(event, context):
    for record in event.get('Records'):
        uploaded_s3_file_key = unquote(record.get('s3').get('object').get('key'))
        print('Processing for s3 file key: {}'.format(uploaded_s3_file_key))
        parse_s3_xml_file_to_sheet(uploaded_s3_file_key)


def handler_bulk_parse_xml_files(event, context):
    days_back = int(event.get('days_back', 1))
    for key in get_matching_s3_keys(settings.S3_BUCKET_NAME, prefix=settings.S3_ROOT_DIR, days_back=days_back):
        print('Processing for s3 file key: {}'.format(key))
        parse_s3_xml_file_to_sheet(key)
