from datetime import datetime, timezone

import boto3

import settings


def get_matching_s3_keys(bucket, prefix='', suffix='', days_back=None):
    """
    Generate the keys in an S3 bucket.

    :param bucket: Name of the S3 bucket.
    :param prefix: Only fetch keys that start with this prefix (optional).
    :param suffix: Only fetch keys that end with this suffix (optional).
    :param days_back: Only fetch keys that were created in the last days (optional).
    """
    s3 = boto3.client('s3')
    kwargs = {'Bucket': bucket}

    # If the prefix is a single string (not a tuple of strings), we can
    # do the filtering directly in the S3 API.
    if isinstance(prefix, str):
        kwargs['Prefix'] = prefix

    today = datetime.now(timezone.utc)

    while True:

        # The S3 API response is a large blob of metadata.
        # 'Contents' contains information about the listed objects.
        resp = s3.list_objects_v2(**kwargs)

        for obj in resp.get('Contents', []):
            key = obj['Key']
            created_days_ago = (today - obj['LastModified']).days

            if (
                obj['Size'] > 0 # Don't include folders names
                and key.startswith(prefix)
                and key.endswith(suffix)
                and (days_back is None or created_days_ago <= days_back)
            ):
                yield key

        # The S3 API is paginated, returning up to 1000 keys at a time.
        # Pass the continuation token into the next response, until we
        # reach the final page (when this field is missing).
        try:
            kwargs['ContinuationToken'] = resp['NextContinuationToken']
        except KeyError:
            break
