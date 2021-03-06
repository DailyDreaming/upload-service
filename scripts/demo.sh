#!/bin/bash

function usage() {
    cat <<-EOF

Usage: $(basename $0) <deployment>

Deployment = "local", "dev", "staging" or "prod"

EOF
    exit 1
}

[ $# -ne 1 ] && usage

DEPLOYMENT=$1

case ${DEPLOYMENT} in
dev|staging|prod)
    API_URL="https://${API_HOST}/v1"
    ;;
local)
    API_URL="http://localhost:5000/v1"
    DEPLOYMENT=dev
    ;;
esac

if [ -z "${INGEST_API_KEY}" ] ; then
    echo -e "\nPlease source the appropriate config/deployment_secrets.py before running.\n"
    exit 1
fi

UPLOAD_AREA_ID=deadbeef-dead-dead-dead-beeeeeeeeeef

function pause() {
    echo
    echo -n "Press enter to continue..."
    read junk
    echo
}

function run_curl() {
    curl_command=$*
    echo curl ${curl_command}
    curl --silent --dump-header /tmp/header --output /tmp/response -H "Api-Key: ${INGEST_API_KEY}" ${curl_command}
    head -1 /tmp/header
    cat /tmp/response
}

function create() {
    echo "CREATE:"
    run_curl -X POST "${API_URL}/area/${UPLOAD_AREA_ID}"
    urn=`jq -r .urn /tmp/response`
    hca upload select "${urn}"
}

function upload() {
    echo "STAGE A FILE:"
    echo hca upload file LICENSE
    hca upload file LICENSE
}

function put_file() {
    echo "PUT FILE VIA API:"
    echo curl -X PUT -H \"Content-type: application/json\" -d 'sdfjdsllfds' "${API_URL}/area/${UPLOAD_AREA_ID}/foobar2.json"
    curl --silent --dump-header /tmp/header --output /tmp/response  \
         -X PUT \
         -H "Api-Key: ${INGEST_API_KEY}" \
         -H "Content-type: application/json; dcp-type=\"metadata/foo\"" \
         -d 'sdfjdsllfds' \
         "${API_URL}/area/${UPLOAD_AREA_ID}/foobar2.json"
    head -1 /tmp/header
    cat /tmp/response
}

function get_file() {
    echo "GET FILE INFO:"
    echo curl "${API_URL}/area/${UPLOAD_AREA_ID}/foobar2.json"
    curl --silent "${API_URL}/area/${UPLOAD_AREA_ID}/foobar2.json"
}

function list() {
    echo "LIST FILES:"
    echo curl "${API_URL}/area/${UPLOAD_AREA_ID}"
    curl --silent "${API_URL}/area/${UPLOAD_AREA_ID}"
}

function lock() {
    echo "LOCK:"
    run_curl -X POST "${API_URL}/area/${UPLOAD_AREA_ID}/lock"
}

function unlock() {
    echo "UNLOCK:"
    run_curl -X DELETE "${API_URL}/area/${UPLOAD_AREA_ID}/lock"
}

function delete() {
    echo "DELETE:"
    run_curl -X DELETE "${API_URL}/area/${UPLOAD_AREA_ID}"
}

function forget() {
    echo "FORGET:"
    hca upload forget `jq -r .upload.current_area ~/.config/hca/config.json`
}

if [[ "${INGEST_API_KEY}" == "" ]] ; then
    echo "Please set INGEST_API_KEY"
    exit 1
fi

create ; pause
upload ; pause
put_file ; pause
get_file ; pause
list ; pause
lock ; pause
echo "PROVE AREA IS LOCKED:"
upload ; pause
unlock ; pause
upload ; pause
delete ; pause
forget
