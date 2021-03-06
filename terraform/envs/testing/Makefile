DEPLOYMENT_STAGE=testing
TF_STATE_BUCKET=org-humancellatlas-upload-infra
S3_TFVARS_FILE=s3://$(TF_STATE_BUCKET)/terraform/envs/$(DEPLOYMENT_STAGE)/terraform.tfvars

default: plan

init:
	terraform init

plan:
	make retrieve-vars
	terraform plan -detailed-exitcode

apply:
	make retrieve-vars
	terraform apply --backup=-

retrieve-vars:
	aws s3 cp $(S3_TFVARS_FILE) terraform.tfvars

upload-vars:
	aws s3 cp terraform.tfvars $(S3_TFVARS_FILE)

import:
	# These resources are shared between deployments in the same account
	- terraform import module.upload-service.aws_iam_role.AWSBatchServiceRole AWSBatchServiceRole
	- terraform import module.upload-service.aws_iam_role.AmazonEC2SpotFleetRole AmazonEC2SpotFleetRole
	- terraform import module.upload-service.aws_iam_role.ecsInstanceRole ecsInstanceRole
	- terraform import module.upload-service.aws_iam_instance_profile.ecsInstanceRole ecsInstanceRole
	- terraform import module.upload-service.aws_iam_service_linked_role.AWSServiceRoleForEC2Spot arn:aws:iam::861229788715:role/aws-service-role/spot.amazonaws.com/AWSServiceRoleForEC2Spot
	- terraform import module.upload-service.aws_iam_service_linked_role.AWSServiceRoleForEC2SpotFleet arn:aws:iam::861229788715:role/aws-service-role/spotfleet.amazonaws.com/AWSServiceRoleForEC2SpotFleet
