#!/bin/sh

set -e

# This shell script is run once when pushing an application to cloud foundry. It's needed to create a super user on the
# OAuth2 (django) server - which happens only once.
# You can find out more about creating super users on django here: https://docs.djangoproject.com/en/1.11/intro/tutorial02/
#
# To run this script to your cloud foundry application from the cli command you can do:
#   /> cf push my_app_name  -c “bash ./init_db.sh"
# To set the start command to 'null' again you can do:
#   /> cf push my_app_name -c "null"
# To find out more go here: https://docs.cloudfoundry.org/devguide/deploy-apps/start-restart-restage.html

echo "------ Create schema ------"
pipenv run python create_schema.py

echo "------ Create database tables ------"
pipenv run python ras_rm_auth_service/manage.py migrate --noinput
