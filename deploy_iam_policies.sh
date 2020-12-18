#!/usr/bin/env bash
set -o errexit
set -o pipefail
set -o nounset

yell() { echo "$0: $*" >&2; }
die() { yell "$*"; exit 111; }

echo
echo "*************************************************************************"
echo "* This script deploys iam policies for personal roles and service users.*"
echo "* You should have done the steps below before you run this script.      *"
echo "*                                                                       *"
echo "* 1) Modify your policies and policy groups in the *.py files.          *"
echo "* 2) Run the generate_iam_yamls.sh to reproduce iam yamls.              *"
echo "* 3) Submit a PR, get the infra team to review the IAM updates.         *"
echo "* 4) Merge the PR.                                                      *"
echo "* 5) Run this script to deploy the iam prolicies.                       *"
echo "*************************************************************************"
echo

git checkout master && git pull

./cloudformation_validation.sh

read -p "All the templates have been validated. Deploy them (Y/N)?" -n 1 -r
echo  #move to a new line
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    die "No deployment is conducted. Exiting..."
fi

gitUser=$(git config user.name)
gitUser="${gitUser// /-}"


echo "Deploying the validated IAM policies for personal roles"
for profile in ./personal-profiles/*
do
  stack="$(cut -d'/' -f 3 <<< $profile | cut -d'.' -f 1)"
  echo "Start deploying template $profile. Stack name is : personal-iam-$stack."
  aws cloudformation deploy \
    --stack-name personal-iam-"$stack" \
    --template-file "$profile" \
    --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM || true
done

echo "Deploying the validated IAM policies for service users"
for template in ./service-user-stacks/*
do
  stack="$(cut -d'/' -f 3 <<< $template | cut -d'.' -f 1)"
  echo "Start deploying template $template. Stack name is : $stack."
  aws cloudformation deploy \
    --stack-name "$stack" \
    --template-file "$template" \
    --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM || true
done
