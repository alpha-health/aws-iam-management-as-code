"""
This python script defines a PolicyGroup class.
"""


class PolicyGroup():
    def __init__(self, policies=None, policy_groups=None):
        """Initialize the object with policies and policy_groups. Note that PolicyGroup has a nested 
        definition, i.e. a policyGroup can contain other policyGroups. But there is no need to do 
        cycle detections, since the policyGroups are immutable, thus a parent can never refer to its
        child (the child does not exist yet when the parent is initialized), thus cycle does exist."""

        # TODO: permission conflict detection (policies may have conflicts)
        self.policies = policies
        self.policy_groups = policy_groups
        self.policies_dedupped = None

    def flatten(self):
        if self.policies_dedupped is not None:
            return self.policies_dedupped
        self.policies_dedupped = set()
        if self.policies is not None:
            for policy in self.policies:
                self.policies_dedupped.add(policy)
        if self.policy_groups is not None:
            for policy_group in self.policy_groups:
                self.policies_dedupped.update(policy_group.flatten())
        return self.policies_dedupped

    def to_yaml(self, **kargs) -> str:
        """ Convert the policyGroup to a yaml string"""
        flattened = self.flatten()
        yaml_str = ''
        for policy in sorted(list(flattened)):
            yaml_str += policy.to_yaml(**kargs)
        return yaml_str