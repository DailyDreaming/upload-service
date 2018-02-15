output "validation_compute_environment" {
  value = "${aws_batch_compute_environment.validation_compute_env.compute_environment_name}"
}

output "validation_job_q_arn" {
  value = "${aws_batch_job_queue.validation_job_q.arn}"
}

output "validation_job_role_arn" {
  value = "${aws_iam_role.validation_job_role.arn}"
}
