#!/bin/bash

mkdir -p .build/lambdas ; cp -r lambda_handlers .build/lambdas
mkdir -p .build/common_layer ; pipenv requirements > .build/common_layer/requirements.txt
cdk deploy --app="python app.py" --require-approval=never --clean
