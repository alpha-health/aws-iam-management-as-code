"""
This python script defines a PolicyGenerator, which is used to
generates iam yaml files for all the users
"""
import logging
import re
import sys
from collections import defaultdict
from pathlib import (
    Path,
    PurePath,
)

from policy import INDENT

from policy_group import (
    PolicyGroup, )

from personal_role_policy_groups import (
    POLICY_GROUP_TEAMA_PROD,
    POLICY_GROUP_TEAMB_PROD,
    POLICY_GROUP_DEVELOPER_B,
)


from service_policy_groups import (
    POLICY_GROUP_WEB_SERVICE_PROD,
)

# The employee names below need to follow r'[A-Z][a-z]{1,25}[A-Z][a-z]{1,25}'
EMPLOYEES = {
    'DeveloperAa': POLICY_GROUP_TEAMA_PROD,
    'DeveloperBb': POLICY_GROUP_DEVELOPER_B,
    'DeveloperCc': POLICY_GROUP_TEAMB_PROD,
    'DeveloperDd': POLICY_GROUP_TEAMB_PROD,
}

# The services below are not per client.
SERVICES = {
    'ServiceUserProdWeb': POLICY_GROUP_WEB_SERVICE_PROD,
}

# All the policies with the prefixes below are put into separate files.
POLICY_CATEGORY_PREFIX = ['S3', 'SecretManager']

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
LOGGER = logging.getLogger()

IAM_ROOT = '../'
PATH_DEVSERVER_PROFILE_TEMPLATE = Path(
    IAM_ROOT, 'templates/devserver_profile_template.yml')

PATH_SERVICE_USER_TEMPLATE = Path(IAM_ROOT,
                                  'templates/service_user_template.yml')
PATH_POLICY_TEMPLATE = Path(IAM_ROOT, 'templates/policy_template.yml')

PATH_PERSONAL_PROFILES = Path(IAM_ROOT, 'personal-profiles')
PATH_SERVICE_USER_STACKS = Path(IAM_ROOT, 'service-user-stacks')


class PolicyGenerator():
    parameters_devserver = {
        'TemplateFormatVersion': '2010-09-09',
        'PolicyDocumentVersion': '2012-10-17',
        'AssumeRolePolicyDocumentVersion': '2012-10-17',
        'ProfileDescription': '',
        'RoleName': '',
        'InstanceProfileName': '',
        'PolicyReferences': '',
        'Policies': '',
    }

    parameters_service = {
        'TemplateFormatVersion': '2010-09-09',
        'PolicyDocumentVersion': '2012-10-17',
        'StackDescription': '',
        'PolicyName': '',
        'PolicyDescription': '',
        'Effects': '',
        'GroupName': '',
        'UserName': '',
    }

    def __init__(self):
        # For sanity check of name.
        self.name_regex = re.compile(r'[A-Z][a-z]{1,25}[A-Z][a-z]{1,25}')

    def name_sanity_check(self):
        is_valid = True
        for name in EMPLOYEES.keys():
            if not bool(self.name_regex.fullmatch(name)):
                LOGGER.error(name +
                             ' is not compliant with nameing convention. ')
                is_valid = False
        return is_valid

    def run(self):
        self.generate_role_devserver_stacks()
        self.generate_user_service_stacks()

    def generate_user_service_stacks(self):
        with open(PATH_SERVICE_USER_TEMPLATE, 'r', encoding='utf-8') as f:
            service_user_template = f.read()
        for service_name, policy_group in sorted(SERVICES.items()):
            self.parameters_service[
                'StackDescription'] = f"IAM stack for service {service_name}"
            self.parameters_service['PolicyName'] = f"PolicyFor{service_name}"
            self.parameters_service[
                'PolicyDescription'] = f"IAM policy for service {service_name} "
            self.parameters_service['GroupName'] = f"IamGroup{service_name}"
            self.parameters_service['UserName'] = f"{service_name}"
            self.parameters_service['Effects'] = policy_group.to_yaml()
            service_user_stack = service_user_template
            for key, value in self.parameters_service.items():
                service_user_stack = self._template_replace(
                    service_user_stack,
                    key,
                    value,
                )
            with open(
                    PurePath.joinpath(
                        PATH_SERVICE_USER_STACKS,
                        f'service-user-{service_name}.yml',
                    ), 'w') as file:
                file.write(service_user_stack)

    def generate_role_devserver_stacks(self):
        if not self.name_sanity_check():
            LOGGER.error('Exiting ...')
            sys.exit(1)

        with open(PATH_DEVSERVER_PROFILE_TEMPLATE, encoding='utf-8') as f:
            profile_template = f.read()
        with open(PATH_POLICY_TEMPLATE, 'r', encoding='utf-8') as f:
            policy_template = f.read()

        for employee_name, policy_group in sorted(EMPLOYEES.items()):
            profile = self._populate_profile(
                employee_name,
                policy_group,
                profile_template,
                policy_template,
            )
            with open(
                    PurePath.joinpath(
                        PATH_PERSONAL_PROFILES,
                        f'profile-{employee_name}.yml',
                    ), 'w') as file:
                file.write(profile)

    def _populate_profile(
        self,
        employee_name,
        policy_group,
        profile_template,
        policy_template,
    ):
        self.parameters_devserver['RoleName'] = 'PersonalRole' + employee_name
        self.parameters_devserver[
            'InstanceProfileName'] = 'PersonalInstanceProfile' + employee_name
        self.parameters_devserver[
            'ProfileDescription'] = 'Personal IAM Profile for ' + employee_name

        subgroups = defaultdict(list)
        for policy in policy_group.flatten():
            found = False
            for category_name_prefix in POLICY_CATEGORY_PREFIX:
                if policy.name.startswith(category_name_prefix):
                    subgroups[category_name_prefix].append(policy)
                    found = True
                    break
            if not found:
                subgroups['Misc'].append(policy)
        for category_name_prefix, subgroup in sorted(subgroups.items()):
            self.parameters_devserver[
                'PolicyName'] = f'PersonalPolicy{category_name_prefix}{employee_name}'
            self.parameters_devserver[
                'PolicyDescription'] = f'Personal Policy {category_name_prefix} for {employee_name}'
            self.parameters_devserver['Effects'] = self._policy_list_to_yaml(
                subgroup,
                RoleName=self.parameters_devserver['RoleName'],
            )
            python_policy = policy_template
            for key, value in self.parameters_devserver.items():
                python_policy = self._template_replace(
                    python_policy,
                    key,
                    value,
                )
            self.parameters_devserver['Policies'] += python_policy + '\n'
            self.parameters_devserver[
                'PolicyReferences'] += f"{INDENT*4}- !Ref {self.parameters_devserver['PolicyName']}\n"
        self.parameters_devserver[
            'PolicyReferences'] = self.parameters_devserver[
                'PolicyReferences'][0:-1]
        profile = profile_template
        for key, value in self.parameters_devserver.items():
            profile = self._template_replace(
                profile,
                key,
                value,
            )
        self.parameters_devserver['Policies'] = ''
        self.parameters_devserver['PolicyReferences'] = ''
        return profile

    def _template_replace(self, template, key, value):
        return template.replace("{{{}}}".format(str(key)), value)

    def _policy_list_to_yaml(self, policies, **kargs):
        return ''.join(
            [policy.to_yaml(**kargs) for policy in sorted(policies)])


if __name__ == '__main__':
    policy_generator = PolicyGenerator()
    policy_generator.run()
