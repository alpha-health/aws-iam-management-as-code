"""
This python script contains the policies related to S3.
"""

from policy import (Policy, S3ReadPolicy, S3WritePolicy)

POLICY_SECRETMANAGER_BOX_READONLY = Policy(
    'SecretManagerBoxReadOnly',
    'Allow',
    [
        'secretsmanager:GetSecretValue',
        'secretsmanager:DescribeSecret',
        'secretsmanager:ListSecrets',
        'secretsmanager:TagResource',
    ],
    [
        'arn:aws:secretsmanager:*:*:secret:Box/*',
    ],
)

POLICY_S3_READ_OPERATIONSA_BUCKET = S3ReadPolicy(
    'S3AllowReadOnBucketOperationsa',
    [
        'arn:aws:s3:::operationsa',
        'arn:aws:s3:::operationsa/*',
    ],
)

POLICY_S3_READ_OPERATIONSB_BUCKET = S3ReadPolicy(
    'S3AllowReadOnBucketOperationsb',
    [
        'arn:aws:s3:::operationsb',
        'arn:aws:s3:::operationsb/*',
    ],
)

POLICY_S3_WRITE_OPERATIONSA_BUCKET = S3WritePolicy(
    'S3AllowWriteOnBucketOperationsa',
    [
        'arn:aws:s3:::operationsa/*',
    ],
)

POLICY_S3_WRITE_OPERATIONSB_BUCKET = S3WritePolicy(
    'S3AllowWriteOnBucketOperationsb',
    [
        'arn:aws:s3:::operationsb/*',
    ],
)

POLICY_AURORA_DATA_API_ALLOW_ALL = Policy(
    'AuroraDataApiAllowAll',
    'Allow',
    [
        'rds-data:BatchExecuteStatement',
        'rds-data:BeginTransaction',
        'rds-data:CommitTransaction',
        'rds-data:ExecuteStatement',
        'rds-data:RollbackTransaction',
    ],
    [
        '*',
    ],
)