import logging
import os
from datetime import timedelta, datetime

import boto3
import settings
from utils.ftp_connection import open_ftp_connection


def remove_old_files_from_ftp(days_back=30, dry_run=True):
    """
    Delete files older than days_back ago if they are in s3
    """
    ftp_connection = open_ftp_connection(
        settings.FTP_HOST,
        settings.FTP_PORT,
        settings.EDITRADE_FTP_USERNAME,
        settings.EDITRADE_FTP_PASSWORD,
    )

    for file in ftp_connection.listdir_attr(settings.FTP_ROOT_DIR):
        if file.st_mtime >= (datetime.today() - timedelta(days=days_back)).timestamp():
            continue

        filename = file.filename
        ftp_file_path = os.path.join(settings.FTP_ROOT_DIR, filename)
        s3_file_path = os.path.join(settings.S3_ROOT_DIR, filename)

        s3_connection = boto3.client("s3")
        try:
            s3_connection.head_object(Bucket=settings.S3_BUCKET_NAME, Key=s3_file_path)
        except Exception as e:
            # Case that file does not exist
            logging.warning(
                'File "{}" does not exist at s3 location "{}"'.format(
                    ftp_file_path, s3_file_path
                )
            )
            continue

        if not dry_run:
            logging.info("Deleting file {}".format(ftp_file_path))
            ftp_connection.remove(ftp_file_path)
        else:
            logging.info("SKIPPING - Dry Run: Deleting file {}".format(ftp_file_path))
        logging.info("Deleting file {}".format(ftp_file_path))
