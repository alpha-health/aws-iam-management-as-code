"""
This python script defines the policy groups related to engineers' devservers.
"""

from policy_group import PolicyGroup
from all_policies import (
    POLICY_SECRETMANAGER_BOX_READONLY,
    POLICY_S3_READ_OPERATIONSA_BUCKET,
    POLICY_S3_READ_OPERATIONSB_BUCKET,
    POLICY_S3_WRITE_OPERATIONSA_BUCKET,
    POLICY_S3_WRITE_OPERATIONSB_BUCKET,
)

POLICY_GROUP_BASE = PolicyGroup(policies=[
    POLICY_SECRETMANAGER_BOX_READONLY,
])

POLICY_GROUP_TEAMA_DEV = PolicyGroup(
    policies=[
        POLICY_S3_READ_OPERATIONSA_BUCKET,
    ],
    policy_groups=[
        POLICY_GROUP_BASE,
    ],
)

POLICY_GROUP_TEAMA_PROD = PolicyGroup(
    policies=[
        POLICY_S3_WRITE_OPERATIONSA_BUCKET,
    ],
    policy_groups=[
        POLICY_GROUP_TEAMA_DEV,
    ],
)

POLICY_GROUP_TEAMB_DEV = PolicyGroup(
    policies=[
        POLICY_S3_READ_OPERATIONSB_BUCKET,
    ],
    policy_groups=[
        POLICY_GROUP_BASE,
    ],
)

POLICY_GROUP_TEAMB_PROD = PolicyGroup(
    policies=[
        POLICY_S3_WRITE_OPERATIONSB_BUCKET,
    ],
    policy_groups=[
        POLICY_GROUP_TEAMB_DEV,
    ],
)

POLICY_GROUP_DEVELOPER_B = PolicyGroup(policy_groups=[
    POLICY_GROUP_TEAMA_PROD,
    POLICY_GROUP_TEAMB_DEV,
], )
