#!/usr/bin/env bash

echo "###################################################"
echo "Build local AWS Lambda's execution environment"
echo "###################################################"

sam build -t cloudformation/sam-template.yaml -s . -m src/requirements.txt

echo "###################################################"
echo "Get token from Keycloak client"
echo "###################################################"
GRANT_TYPE="grant_type=client_credentials"
CLIENT="client_id=server-to-server&client_secret=$1"
TOKEN_URL="http://localhost:8081/auth/realms/softcomweb/protocol/openid-connect/token"

ACCESS_TOKEN=$(curl -s --data "${GRANT_TYPE}&${CLIENT}" ${TOKEN_URL} | jq -r .access_token)
echo "Access token: ${ACCESS_TOKEN}"
echo


echo "###################################################"
echo "Invoke auth lambda"
echo "###################################################"
cat <<EOF | sam local invoke "AuthFunction" --event -
{
    "authorizationToken": "Bearer ${ACCESS_TOKEN}",
    "methodArn": "any-arn"
}
EOF
