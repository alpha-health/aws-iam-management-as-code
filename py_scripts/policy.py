"""
This python script defines a Policy class, and a few subclasses.
"""

from typing import List

INDENT = '  '
DEFAULT_INDENT = 5


class Condition():
    def __init__(
        self,
        name,
        operator: str,
        condition_key: str,
        values: List[str],
    ):
        self.name = name
        self.operator = operator
        self.condition_key = condition_key
        self.values = values

    def to_yaml(self, **kargs) -> str:
        """Convert the condition to a yaml string"""
        base_indent = (DEFAULT_INDENT + 2) * INDENT
        name_str = f"\n{base_indent}# {self.name}"
        operator_str = f"\n{base_indent}{self.operator}:"
        condition_str = f"\n{base_indent}{INDENT}{self.condition_key}:"
        values_str = ''
        for value in self.values:
            values_str += f"\n{base_indent}{2*INDENT}- \"{value}\""
        yaml = name_str + operator_str + condition_str + values_str
        for k, v in kargs.items():
            self._template_replace(yaml, k, v)
        return yaml

    def __lt__(self, other):
        return self.name < other.name

    def _template_replace(self, template, key, value):
        return template.replace("{{{}}}".format(str(key)), value)


class Policy():
    def __init__(
        self,
        name: str,
        effect: str,
        actions: List[str],
        resources: List[str],
        conditions: List[Condition] = None,
    ):
        """Initialize the Policy object"""
        self.name = name
        self.effect = effect
        self.actions = actions
        if isinstance(actions, str):
            raise ValueError("Actions must be a list, got %r." % actions)
        self.resources = resources
        self.conditions = conditions

    def to_yaml(self, **kargs) -> str:
        """Convert the policy to a yaml string"""
        base_indent = DEFAULT_INDENT * INDENT
        name_str = f"\n{base_indent}# {self.name}"
        effect_str = f"\n{base_indent}- Effect: \"{self.effect}\""
        action_str = ''
        for action in self.actions:
            action_str += f"\n{base_indent}{2*INDENT}- \"{action}\""
        action_str = f"\n{base_indent}{INDENT}Action:{action_str}"
        resource_str = ''
        for resource in self.resources:
            resource_str += f"\n{base_indent}{2*INDENT}- \"{resource}\""
        resource_str = f"\n{base_indent}{INDENT}Resource:{resource_str}"
        condition_str = ''
        if self.conditions is not None:
            condition_str += f"\n{base_indent}{INDENT}Condition:"
            for condition in self.conditions:
                condition_str += condition.to_yaml()
        yaml = name_str + effect_str + action_str + resource_str + condition_str
        for k, v in kargs.items():
            yaml = self._template_replace(yaml, k, v)
        return yaml

    def __lt__(self, other):
        return self.name < other.name

    def _template_replace(self, template, key, value):
        return template.replace("{{{}}}".format(str(key)), value)


class S3ReadPolicy(Policy):
    def __init__(
        self,
        name: str,
        resources: List[str],
    ):
        """Initialize the S3ReadPolicy object"""
        Policy.__init__(
            self,
            name,
            'Allow',
            [
                's3:GetObject',
                's3:GetObjectAcl',
                's3:GetObjectVersion',
                's3:ListBucket',
                's3:ListObjectVersions',
                's3:GetBucketLocation',
            ],
            resources,
        )


class S3WritePolicy(Policy):
    def __init__(
        self,
        name: str,
        resources: List[str],
    ):
        """Initialize the S3WritePolicy object"""
        Policy.__init__(
            self,
            name,
            'Allow',
            [
                's3:PutObject',
                's3:PutObjectAcl',
            ],
            resources,
        )


class S3DeletePolicy(Policy):
    def __init__(
        self,
        name: str,
        resources: List[str],
    ):
        """Initialize the S3DeletePolicy object"""
        Policy.__init__(
            self,
            name,
            'Allow',
            [
                's3:DeleteObject',
            ],
            resources,
        )


class S3ListBucketPrefixPolicy(Policy):
    """
    Gives ListBucket permission restricted to the given prefix.

    See the AllowListingOfUserFolder example at https://aws.amazon.com/blogs/security/writing-iam-policies-grant-access-to-user-specific-folders-in-an-amazon-s3-bucket/

    This class works for a single bucket and a single prefix.
    For multiple buckets or multiple prefixes, use the base class.
    """
    def __init__(
        self,
        name: str,
        bucket: str,
        prefix: str,
    ):
        super().__init__(name=name,
                         effect="Allow",
                         actions=["s3:ListBucket"],
                         resources=[f"*:*:s3:::{bucket}"],
                         conditions=[
                             Condition(
                                 name=f"RestrictListBucketToPrefix",
                                 operator="StringLike",
                                 condition_key="s3:prefix",
                                 values=[f"{prefix.rstrip('/')}/*"],
                             )
                         ])
