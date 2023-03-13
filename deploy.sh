#!/bin/bash

rm -rf .build
mkdir -p .build/lambdas ; cp -r lambda_handlers .build/lambdas
mkdir -p .build/common_layer ; cp requirements-min.txt .build/common_layer/requirements.txt
cdk deploy --app="python app.py" --require-approval=never --clean
