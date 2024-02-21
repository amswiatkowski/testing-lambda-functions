#!/bin/bash

rm -rf .build
mkdir -p .build/lambdas ; cp -r lambda_handlers .build/lambdas
mkdir -p .build/common_layer ; poetry export --without=dev --without-hashes --format=requirements.txt > .build/common_layer/requirements.txt
cdk deploy --verbose --require-approval=never --clean
