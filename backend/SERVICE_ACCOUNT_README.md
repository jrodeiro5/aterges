# Service Account Configuration
#
# This directory needs your Aterges-specific service account file.
# 
# Steps:
# 1. Follow ATERGES_INDEPENDENT_SETUP.md to create your Google Cloud project
# 2. Create a service account and download the JSON file
# 3. Rename it to: aterges-service-account.json
# 4. Place it in this directory
# 5. Update .env file: GOOGLE_APPLICATION_CREDENTIALS=./aterges-service-account.json
#
# The .gitignore file will automatically exclude *.json files from version control.
