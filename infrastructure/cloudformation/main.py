# needs DB
# needs s3 vpc
# include lambda?
# security group
# Nacl
# add auto shutdown
from typing import Union
import boto3
import logging
import time
import os
import pathlib
import json
os.chdir(pathlib.Path(__file__).parent)
cloudformation = boto3.client("cloudformation")
rds = boto3.client("rds")
iam = boto3.client("iam")

def check_stack_status(stack_name: str) -> str:
    stacks = cloudformation.list_stacks(
        StackStatusFilter=[
            "CREATE_IN_PROGRESS",
            "CREATE_FAILED",
            "CREATE_COMPLETE",
            "ROLLBACK_IN_PROGRESS",
            "ROLLBACK_FAILED",
            "ROLLBACK_COMPLETE",
            "DELETE_IN_PROGRESS",
            "DELETE_FAILED",
            "UPDATE_IN_PROGRESS",
            "UPDATE_COMPLETE_CLEANUP_IN_PROGRESS",
            "UPDATE_COMPLETE",
            "UPDATE_FAILED",
            "UPDATE_ROLLBACK_IN_PROGRESS",
            "UPDATE_ROLLBACK_FAILED",
            "UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS",
            "UPDATE_ROLLBACK_COMPLETE",
            "REVIEW_IN_PROGRESS",
            "IMPORT_IN_PROGRESS",
            "IMPORT_COMPLETE",
            "IMPORT_ROLLBACK_IN_PROGRESS",
            "IMPORT_ROLLBACK_FAILED",
            "IMPORT_ROLLBACK_COMPLETE",
        ]
    )["StackSummaries"]
    for stack in stacks:
        if stack["StackName"] == stack_name:
            return stack["StackStatus"]


def build_stack(stack: str) -> None:
    if check_stack_status(stack) is not None:
        logging.error("Stack already exists")
        raise ValueError("Stack already exists")

    start = time.time()
    cloudformation.create_stack(
        StackName=stack,
        TemplateBody=open("template.yaml").read(),
        OnFailure="DELETE",
        Capabilities=["CAPABILITY_IAM", "CAPABILITY_NAMED_IAM"],
    )

    while check_stack_status(stack) == "CREATE_IN_PROGRESS":
        logging.debug("Waiting for stack")
        time.sleep(5)

    final_status = check_stack_status(stack)
    if final_status != "CREATE_COMPLETE":
        logging.error(f"The formation completed with status: {final_status}.")
        raise ValueError(f"The formation completed with status: {final_status}.")
    logging.info(
        f"Stack creation took {round(time.time() - start, 2)} seconds to complete"
    )


def get_info(stack: str) -> dict[str, Union[int, str]]:
    resources = cloudformation.list_stack_resources(StackName=stack)[
        "StackResourceSummaries"
    ]
    ret = {}
    for resource in resources:
        if resource['ResourceType'] == "AWS::RDS::DBInstance":
            info = rds.describe_db_instances(DBInstanceIdentifier=resource['PhysicalResourceId'])['DBInstances'][0]
            from pprint import pprint
            ret['db'] = {
                'host': info['Endpoint']['Address'],
                'port': info['Endpoint']['Port'],
                'user': info['MasterUsername'],
                'password': 'postgres1',
                'dbname': info['DBName']
            }
        if resource['ResourceType'] == "AWS::IAM::User":
            creds = iam.create_access_key(UserName=resource['PhysicalResourceId'])["AccessKey"]
            ret['user'] = {"access_key": creds["AccessKeyId"], "secret_key": creds["SecretAccessKey"]}

    with open("../../env.json", "w") as f:
        json.dump(ret, f, indent=4)


def main(stack: str) -> None:
    build_stack(stack)
    get_info(stack)


if __name__ == '__main__':
    main("test2")
