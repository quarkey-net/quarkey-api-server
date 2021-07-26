#!/usr/bin/python3

import sys, os, platform, crypt

if '__main__' == __name__:

	os.system("apt update && apt install python3-venv")
	API_PROJECT_DIR = os.environ.get('API_PROJECT_DIR')
	API_DEPLOY_MOD = os.environ.get('API_DEPLOY_MOD')
	API_PROJECT_NAME = os.environ.get('API_PROJECT_NAME')
	API_INTERN_PORT = os.environ.get('API_PROJECT_NAME')
	API_EXEC_USER_PASSWD = os.environ.get('API_EXEC_USER_PASSWD')

	username = API_PROJECT_NAME + API_DEPLOY_MOD

	os.system(f"useradd -m {username} -p {API_EXEC_USER_PASSWD}")