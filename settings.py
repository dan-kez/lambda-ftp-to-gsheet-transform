import os
import json

USE_PARAMETER_STORE = os.getenv('USE_PARAMETER_STORE', False)

S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME', 'kez-test-mac-shipping-xml-backup')
S3_ROOT_DIR = 'EDITRADEOUT/'  # S3 paths do not start with a leading /

FTP_HOST = os.getenv('FTP_HOST', 'ftphost.editrade.com')
FTP_USERNAME = os.getenv('FTP_USERNAME')
FTP_PASSWORD = os.getenv('FTP_PASSWORD')
FTP_ROOT_DIR = os.getenv('FTP_ROOT_DIR', '/Usr/macship/EDITRADEOUT')
FTP_PORT = int(os.getenv('FTP_PORT', 22))

CHUNK_SIZE = 6291456

GOOGLE_SHEET_NAME = os.getenv('GOOGLE_SHEET_NAME', 'Test File Kez')
GOOGLE_SERVICE_ACCOUNT_CREDENTIAL_JSON = json.loads(os.getenv('GOOGLE_SERVICE_ACCOUNT_CREDENTIAL_JSON', '{}'))

# Low effort way to use parameter store only in prod
if USE_PARAMETER_STORE:
    import boto3

    client = boto3.client('ssm', region_name='us-east-1')


    def get_secret(key):
        resp = client.get_parameter(
            Name=key,
            WithDecryption=True
        )
        return resp['Parameter']['Value']


    FTP_USERNAME = get_secret('FTP_USERNAME')
    FTP_PASSWORD = get_secret('FTP_PASSWORD')
    GOOGLE_SERVICE_ACCOUNT_CREDENTIAL_JSON = json.loads(get_secret('GOOGLE_SERVICE_ACCOUNT_CREDENTIAL_JSON'))