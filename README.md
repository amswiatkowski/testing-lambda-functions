
# Testing Lambda functions

This is a simple project showing how to test Lambda functions with different approaches.

Before you start you need AWS CDK and pipenv installed:

```shell
npm install -g aws-cdk
pip install pipenv
```

Next clone the project and install the requirements:

```shell
pipenv install --dev
```

Login to your AWS account and deploy the stack from this project:
```shell
aws configure sso
export AWS_PROFILE=NAME_OF_YOUR_PROFILE
cdk bootstrap
./deploy.sh
```
# Running unit tests
```shell
pytest -vv ./unit
```
Enjoy!
