"""
This python script defines the policy groups related to services.
"""
from policy_group import PolicyGroup
from all_policies import (
    POLICY_AURORA_DATA_API_ALLOW_ALL,
    POLICY_SECRETMANAGER_BOX_READONLY,
)


POLICY_GROUP_ALL_SERVICES_BASE = PolicyGroup(policies=[
    POLICY_SECRETMANAGER_BOX_READONLY,
])

POLICY_GROUP_WEB_SERVICE_PROD = PolicyGroup(
    policies=[
        POLICY_AURORA_DATA_API_ALLOW_ALL,
    ],
    policy_groups=[
        POLICY_GROUP_ALL_SERVICES_BASE,
    ],
)
