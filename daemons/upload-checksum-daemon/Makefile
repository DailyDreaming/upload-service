include ../../common.mk
.PHONY: install build stage deploy clobber

LAMBDA_NAME=checksum_daemon
ZIP_FILE=$(LAMBDA_NAME).zip
BUCKET=$(BUCKET_NAME_PREFIX)lambda-deployment-$(DEPLOYMENT_STAGE)
STAGED_FILE_KEY=$(LAMBDA_NAME)/$(ZIP_FILE)

default: build

install:
	virtualenv -p python3 venv
	. venv/bin/activate && pip install -r requirements.txt --upgrade

build:
	rm -rf target
	mkdir target
	pip install -r requirements.txt -t target/ --upgrade

	cp -R vendor.in/* target/

	cp -R ../../upload target/
	cp -R *.py target/
	# build.zip contains the psycopg2-3.6 package downloaded from https://github.com/jkehler/awslambda-psycopg2
	# and renamed psycopg2
	unzip build.zip
	cp -R build/ target/
	rm -rf build
	shopt -s nullglob; for wheel in vendor.in/*/*.whl; do unzip -q -o -d vendor $$wheel; done

	cp -R vendor/* target/
	cd target && zip -r ../$(ZIP_FILE) .

stage: build
	aws s3 cp $(ZIP_FILE) s3://$(BUCKET)/$(STAGED_FILE_KEY)

deploy: stage
	aws lambda update-function-code --function-name dcp-upload-csum-$(DEPLOYMENT_STAGE) --s3-bucket $(BUCKET) --s3-key $(STAGED_FILE_KEY)

clobber: ;
