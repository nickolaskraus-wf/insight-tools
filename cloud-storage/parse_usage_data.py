import os
from collections import defaultdict

from google.cloud import storage
from google.cloud import exceptions


def implicit():
    """
    If you don't specify credentials when constructing the client, the client
    library will look for credentials in the environment.

    Environment variable: GOOGLE_APPLICATION_CREDENTIALS
    :return: Client
    """
    storage_client = storage.Client()

    return storage_client


def explicit():
    """
    Explicitly use service account credentials by specifying the private key
    file. All clients in google-cloud-python have this helper.

    :return: Client
    """
    storage_client = storage.Client.from_service_account_json(
        'sandbox-96d461c1d38d.json')

    return storage_client


def list_blobs(storage_client, bucket_name):
    """
    Lists all the blobs in the bucket.

    :param: google.cloud.storage.client.Client
    :param: Google Cloud Storage bucket name
    :return: Iterator of all Blob in bucket passed as an argument
    :rtype: Iterator
    """
    bucket = storage_client.bucket(bucket_name)

    blobs = bucket.list_blobs()

    return blobs


def view_bucket_iam_members(storage_client, bucket_name):
    """
    Retrieve the IAM policy for the bucket.

    :param: google.cloud.storage.client.Client
    :param: Google Cloud Storage bucket name
    :return: the policy instance, based on the resource returned from the getIamPolicy API request
    :rtype: google.cloud.iam.Policy
    """
    bucket = storage_client.bucket(bucket_name)

    policy = bucket.get_iam_policy()

    return policy


def download_blob(storage_client, bucket_name, source_blob, destination_file):
    """
    Downloads a blob from the bucket.

    :param: google.cloud.storage.client.Client
    :param: Google Cloud Storage bucket name
    :param source_blob: blob name
    :param destination_file: file name
    :return:
    """
    bucket = storage_client.get_bucket(bucket_name)

    blob = bucket.blob(source_blob)

    with open(destination_file, 'wb') as file_obj:
        blob.download_to_file(file_obj)

    print('Blob {} downloaded to {}.'.format(
        source_blob,
        destination_file))

    file_obj.close()


def parse_usage_data():
    return ''


def main():
    # export credentials
    # export GOOGLE_APPLICATION_CREDENTIALS=<path_to_service_account_file>

    storage_client = implicit()
    # storage_client = explicit()

    # Make an authenticated API request
    buckets = list(storage_client.list_buckets())
    for bucket in buckets:
        print(buckets)

    bucket_name = 'sandbox-158601-test-bucket'
    blob_names = []

    # get bucket
    bucket = None
    try:
        bucket = storage_client.get_bucket(bucket_name)
    except exceptions.NotFound as e:
        print('Error: %s' % e)

    # iterate blobs
    blobs = list_blobs(storage_client, bucket_name)
    for blob in list(blobs):
        blob_names.append(blob.name)
        print(blob)

    # list roles
    policy = view_bucket_iam_members(storage_client, bucket_name)
    for role in policy:
        members = policy[role]
        print('Role: {}, Members: {}'.format(role, members))

    dir_name = 'usage_data/'
    # download blobs to usage_data
    for blob_name in blob_names:
        destination_file = dir_name + blob_name
        download_blob(storage_client, bucket_name, blob_name, destination_file)


if __name__ == '__main__':
    main()
