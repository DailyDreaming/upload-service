#!/usr/bin/env python3.6

import uuid
from unittest.mock import patch

from ... import UploadTestCaseUsingMockAWS, EnvironmentSetup
from . import client_for_test_api_server

from upload.common.uploaded_file import UploadedFile
from upload.common.upload_area import UploadArea
from upload.common.validation_event import ValidationEvent
from upload.common.checksum_event import ChecksumEvent
from upload.common.database import UploadDB
from upload.common.upload_api_client import update_event


class TestUploadApiClient(UploadTestCaseUsingMockAWS):

    def setUp(self):
        super().setUp()
        # Environment
        self.api_key = "unguessable"
        self.environment = {
            'INGEST_API_KEY': self.api_key,
            'INGEST_AMQP_SERVER': 'foo',
            'CSUM_DOCKER_IMAGE': 'bogoimage',
            'API_HOST': 'bogohost'
        }
        self.environmentor = EnvironmentSetup(self.environment)
        self.environmentor.enter()
        # Setup authentication
        self.authentication_header = {'Api-Key': self.api_key}
        # Setup app
        self.client = client_for_test_api_server()

    def tearDown(self):
        super().tearDown()
        self.environmentor.exit()

    def _create_area(self):
        area_uuid = str(uuid.uuid4())
        self.client.post(f"/v1/area/{area_uuid}", headers=self.authentication_header)
        return area_uuid

    @patch('upload.lambdas.api_server.v1.area.IngestNotifier.format_and_send_notification')
    def test_update_event_with_validation_event(self, mock_format_and_send_notification):

        validation_id = str(uuid.uuid4())
        area_id = self._create_area()
        s3obj = self.mock_upload_file_to_s3(area_id, 'foo.json')
        upload_area = UploadArea(area_id)
        uploaded_file = UploadedFile(upload_area, s3object=s3obj)
        validation_event = ValidationEvent(file_ids=[uploaded_file.db_id],
                                           validation_id=validation_id,
                                           job_id='12345',
                                           status="SCHEDULED")
        validation_event.create_record()
        validation_event.status = "VALIDATING"
        response = update_event(validation_event, uploaded_file.info(), self.client)
        self.assertEqual(204, response.status_code)
        record = UploadDB().get_pg_record("validation", validation_id)
        self.assertEqual("VALIDATING", record["status"])
        self.assertEqual("<class 'datetime.datetime'>", str(type(record.get("validation_started_at"))))
        self.assertEqual(None, record["validation_ended_at"])
        self.assertEqual(None, record.get("results"))

        validation_event.status = "VALIDATED"
        response = update_event(validation_event, uploaded_file.info(), self.client)
        self.assertEqual(204, response.status_code)
        record = UploadDB().get_pg_record("validation", validation_id)
        self.assertEqual("VALIDATED", record["status"])
        self.assertEqual("<class 'datetime.datetime'>", str(type(record.get("validation_started_at"))))
        self.assertEqual("<class 'datetime.datetime'>", str(type(record.get("validation_ended_at"))))
        self.assertEqual(uploaded_file.info(), record.get("results"))

    @patch('upload.lambdas.api_server.v1.area.IngestNotifier.format_and_send_notification')
    def test_update_event_with_checksum_event(self, mock_format_and_send_notification):

        checksum_id = str(uuid.uuid4())
        area_uuid = self._create_area()
        s3obj = self.mock_upload_file_to_s3(area_uuid, 'foo.json')
        upload_area = UploadArea(area_uuid)
        uploaded_file = UploadedFile(upload_area, s3object=s3obj)
        checksum_event = ChecksumEvent(file_id=uploaded_file.db_id,
                                       checksum_id=checksum_id,
                                       job_id='12345',
                                       status="SCHEDULED")
        checksum_event.create_record()

        checksum_event.status = "CHECKSUMMING"
        response = update_event(checksum_event, uploaded_file.info(), self.client)
        self.assertEqual(204, response.status_code)
        record = UploadDB().get_pg_record("checksum", checksum_id)
        self.assertEqual("CHECKSUMMING", record["status"])
        self.assertEqual("<class 'datetime.datetime'>", str(type(record.get("checksum_started_at"))))
        self.assertEqual(None, record["checksum_ended_at"])

        checksum_event.status = "CHECKSUMMED"
        response = update_event(checksum_event, uploaded_file.info(), self.client)
        self.assertEqual(204, response.status_code)
        record = UploadDB().get_pg_record("checksum", checksum_id)
        self.assertEqual("CHECKSUMMED", record["status"])
        self.assertEqual("<class 'datetime.datetime'>", str(type(record.get("checksum_started_at"))))
        self.assertEqual("<class 'datetime.datetime'>", str(type(record.get("checksum_ended_at"))))
