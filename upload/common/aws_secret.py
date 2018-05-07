import boto3
import os
from botocore.errorfactory import ClientError

if not os.environ.get("CONTAINER"):
    secrets_mgr = boto3.client(service_name='secretsmanager')


class AwsSecret:

    """
    Wrapper for AWS secrets.

    Usage:
        secret = AwsSecret(name="my/component/secret")
        secret.update(value='{"foo":"bar"}'
        secret.value
        # -> '{"foo":"bar"}'
        secret.delete()

    Update handles create vs update and undeletion if necessary.
    """

    def __init__(self, name):
        self.name = name
        self.secret_metadata = None
        self._load()

    @property
    def value(self):
        if not self.secret_metadata:
            raise RuntimeError("No such secret")
        if 'DeletedDate' in self.secret_metadata:
            raise RuntimeError("This secret is deleted")
        response = secrets_mgr.get_secret_value(SecretId=self.secret_metadata['ARN'])
        return response['SecretString']

    def update(self, value):
        if not self.secret_metadata:
            secrets_mgr.create_secret(Name=self.name, SecretString=value)
            self._load()
        else:
            self._restore()
            secrets_mgr.put_secret_value(SecretId=self.secret_metadata['ARN'],
                                         SecretString=value)

    def delete(self):
        if not self.secret_metadata:
            raise RuntimeError("No such secret")
        if 'DeletedDate' not in self.secret_metadata:
            secrets_mgr.delete_secret(SecretId=self.secret_metadata['ARN'])
            self._load()

    def _load(self):
        try:
            response = secrets_mgr.describe_secret(SecretId=self.name)
            if response:
                self.secret_metadata = response
        except ClientError as e:
            if e.response['Error']['Code'] != 'ResourceNotFoundException':
                raise e

    def _restore(self):
        if 'DeletedDate' in self.secret_metadata:
            secrets_mgr.restore_secret(SecretId=self.secret_metadata['ARN'])
            self._load()