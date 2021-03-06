resource "aws_secretsmanager_secret" "secrets" {
  name = "dcp/upload/${var.deployment_stage}/secrets"
}

resource "aws_secretsmanager_secret_version" "secrets" {
  secret_id = "${aws_secretsmanager_secret.secrets.id}"
  secret_string = <<SECRETS_JSON
{
  "bucket_name": "${aws_s3_bucket.upload_areas_bucket.bucket}",
  "validation_job_q_arn": "${aws_batch_job_queue.validation_job_q.arn}",
  "validation_job_role_arn": "${aws_iam_role.validation_job_role.arn}",
  "csum_job_q_arn": "${aws_batch_job_queue.csum_job_q.arn}",
  "csum_upload_q_url": "${aws_sqs_queue.upload_queue.id}",
  "area_deletion_q_url": "${aws_sqs_queue.area_deletion_queue.id}",
  "area_deletion_lambda_name": "${aws_lambda_function.area_deletion_lambda.function_name}",
  "csum_job_role_arn": "${aws_iam_role.csum_job_role.arn}",
  "upload_submitter_role_arn": "${aws_iam_role.upload_submitter.arn}",
  "api_key": "${var.ingest_api_key}",
  "slack_webhook": "${var.slack_webhook}",
  "staging_bucket_arn": "${var.staging_bucket_arn}",
  "ingest_api_host": "${var.ingest_api_host}",
  "validation_q_url": "${aws_sqs_queue.validation_queue.id}"
}
SECRETS_JSON
}

resource "aws_secretsmanager_secret" "outgoing_ingest_auth" {
  name = "dcp/upload/${var.deployment_stage}/outgoing_ingest_auth"
}

resource "aws_secretsmanager_secret_version" "outgoing_ingest_auth" {
  secret_id = "${aws_secretsmanager_secret.outgoing_ingest_auth.id}"
  secret_string = <<SECRETS_JSON
{
  "dcp_auth0_audience": "${var.dcp_auth0_audience}",
  "gcp_service_acct_creds": "${var.gcp_service_acct_creds}"
}
SECRETS_JSON
}
