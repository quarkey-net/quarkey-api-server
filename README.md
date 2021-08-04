# REST API Backend for Quarkey Frontend

<center><img src="https://github.com/PowerSaucisse/quarkey-api-server/blob/main/assets/img/quarkey-full.png?raw=true" alt="Quarkey" width="100%"></center>

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/PowerSaucisse/Quarkey-api-server) [![Chat](https://img.shields.io/badge/chat-on%20discord-7289da.svg)](https://discord.gg/PatReunPk5)

## Introduction

_"A RESTful api for the Quarkey password manager and its web application made in VueJS. It will eventually support experimental quantum encryption in its stable version"_

> If you wish to use the API in a public development version you will need to request a development key to activate your account. Please contact us at 
**esteban.ristich@protonmail.com** or notify us on our discord server.

## Quickstart

The API can be built locally. For a precise configuration of the api when it is launched, please refer to the file **utils/configs.py**

> The API requires a postgresql server. The tables to be loaded are specified in the database/sql folder and must be loaded in this order:
> 1. tables.sql
> 2. triggers.sql
> 3. functions.sql

### Linux dependencies (Debian & Ubuntu)

```bash
$ sudo apt update && sudo apt install gcc libev-dev libpq-dev postgresql python3 python3-venv
```

### Building

```bash
# clone development repository
$ git clone git@github.com:PowerSaucisse/quarkey-api-server.git --branch dev

# Move to project
$ cd quarkey-api-server

# Setup virtual environment and packages
$ python -m venv ./venv             
$ source ./venv/bin/activate        # .\venv\Scripts\Activate.ps1 for Windows
$ pip3 install -r requirements.txt  # win_requirements.txt for Windows

# launch
$ python launch.py
```
