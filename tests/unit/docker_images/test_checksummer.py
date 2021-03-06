import unittest
from unittest.mock import patch
import uuid

import boto3

from .. import UploadTestCaseUsingMockAWS, EnvironmentSetup
from ... import FixtureFile

from upload.common.upload_config import UploadConfig


class TestChecksummerDockerImage(UploadTestCaseUsingMockAWS):

    def setUp(self):
        super().setUp()
        UploadConfig.use_env = True
        # Setup environment
        self.environment = {
            'BUCKET_NAME': self.upload_bucket.name,
            'AWS_BATCH_JOB_ID': '1',
            'INGEST_AMQP_SERVER': 'bogoamqp',
            'API_HOST': 'bogohost',
            'CHECKSUM_ID': str(uuid.uuid4()),
            'CONTAINER': 'yes'
        }
        self.environmentor = EnvironmentSetup(self.environment)
        self.environmentor.enter()

    def tearDown(self):
        super().tearDown()
        self.environmentor.exit()

    @patch('upload.docker_images.checksummer.checksummer.Checksummer._update_checksum_event')
    def test_checksummer_checksums(self, mock_update_checksum_event):
        test_file = FixtureFile.factory("foo")
        file_s3_key = f"somearea/{test_file.name}"
        self.create_s3_object(file_s3_key, content=test_file.contents)
        s3_url = f"s3://{self.upload_bucket.name}/{file_s3_key}"

        from upload.docker_images.checksummer.checksummer import Checksummer
        Checksummer([s3_url, test_file.e_tag])

        tagging = boto3.client('s3').get_object_tagging(Bucket=self.upload_bucket.name, Key=file_s3_key)
        self.assertEqual(
            sorted(tagging['TagSet'], key=lambda x: x['Key']),
            test_file.s3_tagset
        )

        self.assertEqual(2, mock_update_checksum_event.call_count)
        self.assertEqual({'status': 'CHECKSUMMING'}, mock_update_checksum_event.call_args_list[0][1])
        self.assertEqual({'status': 'CHECKSUMMED'}, mock_update_checksum_event.call_args_list[1][1])

    @patch('upload.docker_images.checksummer.checksummer.Checksummer._update_checksum_event')
    def test_checksummer__when_file_etag_is_wrong__aborts(self, mock_update_checksum_event):
        test_file = FixtureFile.factory("foo")
        file_s3_key = f"somearea/{test_file.name}"
        self.create_s3_object(file_s3_key, content=test_file.contents)
        s3_url = f"s3://{self.upload_bucket.name}/{file_s3_key}"

        from upload.docker_images.checksummer.checksummer import Checksummer
        Checksummer([s3_url, "the-wrong-etag"])

        mock_update_checksum_event.assert_called_once_with(status='ABORTED')


if __name__ == '__main__':
    unittest.main()
