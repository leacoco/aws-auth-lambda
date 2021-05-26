#!/usr/bin/env bash

APP_NAME="si-auth-function"
BRANCH_NAME=$(git rev-parse --abbrev-ref HEAD)
BRANCH_NAME_NORMALIZED=$(echo $BRANCH_NAME | tr '/' '-')

GITHUB_REPO=$(git remote -v | grep fetch | cut -d'/' -f2 | cut -d' ' -f1 | sed 's/\.git//')

APP_NAME="${APP_NAME}-${PIPELINE_ENVIRONMENT}"

# Ensure deployments: develop -> si-nonlive, master -> si-live
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)


GITHUB_TOKEN=$1
# feature branches can be deployed anywhere ;-)

echo "Deploy cloudformation/pipeline.yaml..."
aws cloudformation deploy \
    --template-file cloudformation/pipeline.yaml \
    --stack-name ${APP_NAME}-pl \
    --parameter-overrides \
        AppName=${APP_NAME} \
        Environment=live \
        GithubRepo=${GITHUB_REPO} \
        GithubBranch=${BRANCH_NAME} \
        GithubToken=${GITHUB_TOKEN} \
    --capabilities CAPABILITY_NAMED_IAM

echo
echo "Environment: ${ENVIRONMENT}"
echo -n "Codepipeline Url: "
aws cloudformation describe-stacks \
    --stack-name ${APP_NAME}-pl \
    --query Stacks[0].Outputs[?OutputKey==\'PipelineUrl\'].OutputValue \
    --output text
