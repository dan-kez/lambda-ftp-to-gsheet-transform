import logging
import math
import time
from functools import cached_property

import boto3

import settings
from utils.ftp_connection import open_ftp_connection


class EditradeFTPService(object):
    ftp_host = settings.FTP_HOST
    ftp_port = settings.FTP_PORT
    ftp_username = settings.EDITRADE_FTP_USERNAME
    ftp_password = settings.EDITRADE_FTP_PASSWORD

    s3_bucket = settings.S3_BUCKET_NAME

    chunk_size = settings.CHUNK_SIZE

    @cached_property
    def s3_connection(self):
        return boto3.client("s3")

    def transfer_file_from_ftp_to_s3(
        self, ftp_file_path, s3_file_path,
    ):
        ftp_connection = open_ftp_connection(
            self.ftp_host, self.ftp_port, self.ftp_username, self.ftp_password
        )
        ftp_file = ftp_connection.file(ftp_file_path, "r")

        ftp_file_size = ftp_file._get_size()

        try:
            s3_file = self.s3_connection.head_object(
                Bucket=self.s3_bucket, Key=s3_file_path
            )
            if s3_file["ContentLength"] == ftp_file_size:
                logging.info(
                    "{} | File Already Exists in S3 bucket".format(ftp_file_path)
                )
                ftp_file.close()
                return
        except Exception as e:
            pass

        if ftp_file_size <= int(self.chunk_size):
            # upload file in one go
            logging.info(
                "{} | Transferring complete File from FTP to S3...".format(
                    ftp_file_path
                )
            )
            self.s3_connection.upload_fileobj(ftp_file, self.s3_bucket, s3_file_path)
            logging.info(
                "{} | Successfully Transferred file from FTP to S3!".format(
                    ftp_file_path
                )
            )
            ftp_file.close()

        else:
            logging.info(
                "{} | Transferring File from FTP to S3 in chunks...".format(
                    ftp_file_path
                )
            )
            # upload file in chunks
            chunk_count = int(math.ceil(ftp_file_size / float(self.chunk_size)))
            multipart_upload = self.s3_connection.create_multipart_upload(
                Bucket=self.s3_bucket, Key=s3_file_path
            )
            parts = []
            for i in range(chunk_count):
                logging.info(
                    "{} | Transferring chunk {}...".format(ftp_file_path, i + 1)
                )
                part = self._transfer_chunk_from_ftp_to_s3(
                    ftp_file, multipart_upload, s3_file_path, i + 1,
                )
                parts.append(part)
                logging.info(
                    "{} | Chunk {} Transferred Successfully!".format(
                        ftp_file_path, i + 1
                    )
                )

            part_info = {"Parts": parts}
            self.s3_connection.complete_multipart_upload(
                Bucket=self.s3_bucket,
                Key=s3_file_path,
                UploadId=multipart_upload["UploadId"],
                MultipartUpload=part_info,
            )
            logging.info(
                "{} | All chunks Transferred to S3 bucket! File Transfer successful!".format(
                    ftp_file_path
                )
            )
            ftp_file.close()

    def _transfer_chunk_from_ftp_to_s3(
        self, ftp_file, multipart_upload, s3_file_path, part_number,
    ):
        start_time = time.time()
        chunk = ftp_file.read(int(self.chunk_size))
        part = self.s3_connection.upload_part(
            Bucket=self.s3_bucket,
            Key=s3_file_path,
            PartNumber=part_number,
            UploadId=multipart_upload["UploadId"],
            Body=chunk,
        )
        end_time = time.time()
        total_seconds = end_time - start_time
        logging.info(
            "speed is {} kb/s total seconds taken {}".format(
                math.ceil((int(self.chunk_size) / 1024) / total_seconds), total_seconds
            )
        )
        part_output = {"PartNumber": part_number, "ETag": part["ETag"]}
        return part_output


editrade_ftp_service = EditradeFTPService()
