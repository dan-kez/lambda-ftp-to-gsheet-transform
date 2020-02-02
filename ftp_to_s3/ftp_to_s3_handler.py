import logging
import math
import os
import time
from datetime import timedelta, datetime

import boto3

import settings
from ftp_to_s3.ftp_connection import open_ftp_connection


def transfer_chunk_from_ftp_to_s3(
        ftp_file,
        s3_connection,
        multipart_upload,
        bucket_name,
        s3_file_path,
        part_number,
        chunk_size
):
    start_time = time.time()
    chunk = ftp_file.read(int(chunk_size))
    part = s3_connection.upload_part(
        Bucket=bucket_name,
        Key=s3_file_path,
        PartNumber=part_number,
        UploadId=multipart_upload['UploadId'],
        Body=chunk,
    )
    end_time = time.time()
    total_seconds = end_time - start_time
    logging.info('speed is {} kb/s total seconds taken {}'.format(math.ceil((int(chunk_size) / 1024) / total_seconds),
                                                           total_seconds))
    part_output = {
        'PartNumber': part_number,
        'ETag': part['ETag']
    }
    return part_output


def transfer_file_from_ftp_to_s3(bucket_name, ftp_file_path, s3_file_path, ftp_username, ftp_password, chunk_size):
    ftp_connection = open_ftp_connection(settings.FTP_HOST, settings.FTP_PORT, ftp_username, ftp_password)
    ftp_file = ftp_connection.file(ftp_file_path, 'r')
    s3_connection = boto3.client('s3')
    ftp_file_size = ftp_file._get_size()

    try:
        s3_file = s3_connection.head_object(Bucket=bucket_name, Key=s3_file_path)
        if s3_file['ContentLength'] == ftp_file_size:
            logging.info('{} | File Already Exists in S3 bucket'.format(ftp_file_path))
            ftp_file.close()
            return
    except Exception as e:
        pass

    if ftp_file_size <= int(chunk_size):
        # upload file in one go
        logging.info('{} | Transferring complete File from FTP to S3...'.format(ftp_file_path))
        s3_connection.upload_fileobj(ftp_file, bucket_name, s3_file_path)
        logging.info('{} | Successfully Transferred file from FTP to S3!'.format(ftp_file_path))
        ftp_file.close()

    else:
        logging.info('{} | Transferring File from FTP to S3 in chunks...'.format(ftp_file_path))
        # upload file in chunks
        chunk_count = int(math.ceil(ftp_file_size / float(chunk_size)))
        multipart_upload = s3_connection.create_multipart_upload(Bucket=bucket_name, Key=s3_file_path)
        parts = []
        for i in range(chunk_count):
            logging.info('{} | Transferring chunk {}...'.format(ftp_file_path, i + 1))
            part = transfer_chunk_from_ftp_to_s3(
                ftp_file,
                s3_connection,
                multipart_upload,
                bucket_name,
                s3_file_path,
                i + 1,
                chunk_size
            )
            parts.append(part)
            logging.info('{} | Chunk {} Transferred Successfully!'.format(ftp_file_path, i + 1))

        part_info = {
            'Parts': parts
        }
        s3_connection.complete_multipart_upload(
            Bucket=bucket_name,
            Key=s3_file_path,
            UploadId=multipart_upload['UploadId'],
            MultipartUpload=part_info
        )
        logging.info('{} | All chunks Transferred to S3 bucket! File Transfer successful!'.format(ftp_file_path))
        ftp_file.close()


def transfer_all_editrade_files_to_s3(days_back=1):
    ftp_connection = open_ftp_connection(settings.FTP_HOST, settings.FTP_PORT, settings.EDITRADE_FTP_USERNAME,
                                         settings.EDITRADE_FTP_PASSWORD)

    for file in ftp_connection.listdir_attr(settings.FTP_ROOT_DIR):
        # We only care about files in the last `days_back` days
        if file.st_mtime < (datetime.today() - timedelta(days=days_back)).timestamp():
            continue

        filename = file.filename
        ftp_file_path = os.path.join(settings.FTP_ROOT_DIR, filename)
        destination_s3_file_path = os.path.join(settings.S3_ROOT_DIR, filename)

        transfer_file_from_ftp_to_s3(
            settings.S3_BUCKET_NAME,
            ftp_file_path,
            destination_s3_file_path,
            settings.EDITRADE_FTP_USERNAME,
            settings.EDITRADE_FTP_PASSWORD,
            settings.CHUNK_SIZE
        )
