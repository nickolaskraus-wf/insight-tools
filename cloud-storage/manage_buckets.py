"""
Description:
  Proof of Concept for Google Cloud Storage API.

Usage:

"""

from google.cloud import storage


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


def main():
    # export credentials
    # export GOOGLE_APPLICATION_CREDENTIALS=<path_to_service_account_file>

    storage_client = implicit()
    # storage_client = explicit()

    # Make an authenticated API request
    buckets = list(storage_client.list_buckets())
    print(buckets)


if __name__ == '__main__':
    main()
