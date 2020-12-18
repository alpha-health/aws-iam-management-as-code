#!/usr/bin/env bash

# Do the CloudFormation validations
valid=1
for profile in ./personal-profiles/*
do
  echo "Validating the cloudformation template: $profile ..."
  aws cloudformation validate-template --template-body file://"$profile" > /dev/null 2>&1
  if [ $? -ne 0 ]; then
    echo "$profile failed validation."
    valid=0
  else
    echo "$profile passed validation."
  fi
done

for service_user in ./service-user-stacks/*
do
  echo "Validating the cloudformation template: $service_user ..."
  aws cloudformation validate-template --template-body file://"$service_user" > /dev/null 2>&1
  if [ $? -ne 0 ]; then
    echo "$service_user failed validation."
    valid=0
  else
    echo "$service_user passed validation."
  fi
done


printf "\n"

if [ $valid == 1 ]; then
    echo "All validations passed."
else
    echo "Some validations failed. Please fix."
    exit 1
fi
