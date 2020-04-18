import json
import os

from functions.custom_lambda_exceptions import NoFilesToProcess

STAGE = os.getenv("STAGE", "dev")
DYNAMO_TABLE_PREFIX = os.getenv("DYNAMO_TABLE_PREFIX", f"gen-editrade-sync__{STAGE}__")
# If set to falsey value default to None
DYNAMO_HOST = os.getenv("DYNAMO_HOST", "http://localhost:3333") or None


USE_PARAMETER_STORE = os.getenv("USE_PARAMETER_STORE", False)

S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
S3_ROOT_DIR = "EDITRADEOUT/"  # S3 paths do not start with a leading /

FTP_HOST = os.getenv("FTP_HOST", "ftphost.editrade.com")
EDITRADE_FTP_USERNAME = os.getenv("EDITRADE_FTP_USERNAME")
EDITRADE_FTP_PASSWORD = os.getenv("EDITRADE_FTP_PASSWORD")
FTP_ROOT_DIR = os.getenv("FTP_ROOT_DIR", "/Usr/macship/EDITRADEOUT/")
FTP_PORT = int(os.getenv("FTP_PORT", 22))

CHUNK_SIZE = 6291456

GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME", "MAC - AMAZON CUSTOMS SYNC")
GOOGLE_WORKSHEET_NAME = "RAW DATA - DO NOT EDIT"
GOOGLE_SERVICE_ACCOUNT_CREDENTIAL_JSON = json.loads(
    os.getenv("GOOGLE_SERVICE_ACCOUNT_CREDENTIAL_JSON", "{}")
)

# Low effort way to use parameter store only in prod
if USE_PARAMETER_STORE:
    import boto3

    client = boto3.client("ssm", region_name="us-east-1")

    def get_secret(key):
        resp = client.get_parameter(Name=key, WithDecryption=True)
        return resp["Parameter"]["Value"]

    EDITRADE_FTP_USERNAME = get_secret("EDITRADE_FTP_USERNAME")
    EDITRADE_FTP_PASSWORD = get_secret("EDITRADE_FTP_PASSWORD")
    GOOGLE_SERVICE_ACCOUNT_CREDENTIAL_JSON = json.loads(
        get_secret("GOOGLE_SERVICE_ACCOUNT_CREDENTIAL_JSON")
    )

    SENTRY_DSN = get_secret("SENTRY_DSN")

    if SENTRY_DSN:
        import sentry_sdk
        from sentry_sdk.integrations.aws_lambda import AwsLambdaIntegration

        def ignore_known_exceptions(event, hint):
            if "exc_info" in hint:
                exc_type, exc_value, tb = hint["exc_info"]
                # Ignore NoFilesToProcess as it's a handled short circuit error
                if isinstance(exc_value, (NoFilesToProcess,)):
                    return None
            return event

        sentry_sdk.init(
            SENTRY_DSN,
            integrations=[AwsLambdaIntegration()],
            before_send=ignore_known_exceptions,
        )
