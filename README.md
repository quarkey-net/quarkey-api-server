# REST API Backend for Quarkey Frontend

<center><img src="/assets/img/quarkey-full.png?raw=true" alt="Quarkey" width="100%"></center>

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/PowerSaucisse/Quarkey-api-server) [![Chat](https://img.shields.io/badge/chat-on%20discord-7289da.svg)](https://discord.gg/PatReunPk5)

## Introduction

_"A RESTful api for the Quarkey password manager and its web application made in VueJS. It will eventually support experimental quantum encryption in its stable version"_

> If you wish to use the API in a public development version you will need to request a development key to activate your account. Please contact us at 
**esteban.ristich@protonmail.com** or notify us on our discord server.

## Table of contents
- [REST API Backend for Quarkey Frontend](#rest-api-backend-for-quarkey-frontend)
  - [Introduction](#introduction)
  - [Table of contents](#table-of-contents)
  - [Quickstart](#quickstart)
    - [Linux dependencies (Debian & Ubuntu)](#linux-dependencies-debian--ubuntu)
    - [Building](#building)
  - [Documentation](#documentation)
    - [Create account](#create-account)
    - [Login to account](#login-to-account)
    - [Create password item](#create-password-item)
    - [Get password item](#get-password-item)
    - [Delete password item](#delete-password-item)
    - [Create tag item](#create-tag-item)
    - [Get tag item](#get-tag-item)
    - [Delete tag item](#delete-tag-item)
    - [Link password to tag](#link-password-to-tag)
    - [Unlink password from tag](#unlink-password-from-tag)
    - [Create tester key](#create-tester-key)
  - [License](#license)

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

## Documentation

There is currently no domain name assigned to the service. However, a Heroku version is hosted in order to perform security tests and audits. If you wish to contribute, you can request key from the following address:
  - esteban.ristich@protonmail.com
  - regis.brasme@gmail.com

> The API currently only supports JSON. So please define in your header the following key and value `'Content-Type': 'application/json'` and your token `'Authorization': 'YOUR_TOKEN'`. This token will be needed to access all resources, except :
> - ```http://quarkey.herokuapp.com/api/auth/register```
> - ```http://quarkey.herokuapp.com/api/auth/login```

### Create account

- Method : ```POST```
- Request : ```http://quarkey.herokuapp.com/api/auth/register```
- Parameter :
  - username  : ```TEXT``` _Username take minimum 3 characters and 24 max with numbers but no special characters execpt underscore_
  - firstname : ```TEXT``` _Firstname take minimum 2 characters and 20 max_
  - lastname  : ```TEXT``` _Lastname take minimum 2 characters and 20 max_
  - email     : ```TEXT```_Take email format_
  - password  : ```TEXT``` _Password must have at least one capital letter and one special character and one number. He must have also 8 minimum characters_
  - key       : ```TEXT``` _20 characters key_
- Body :

  ```json
      {
          "username" : "esteban",
          "firstname": "Esteban",
          "lastname" : "Ristich",
          "email"    : "esteban.ristich@protonmail.com",
          "password" : "Motdepasse#38",
          "key"      : "<TESTER KEY>"
      }
  ```

### Login to account
>_For security and caching reasons, login requests are made via the POST method._

- Method : ```POST```
- Request : ```http://quarkey.herokuapp.com/api/auth/login```
- Body :

  ```json
  {
    "username": "esteban",
    "password": "Motdepasse#38"
  }
  ```

- Return :

  ```json
  {
    "title": "OK",
    "description": "success to login",
    "content": {"token": "<YOUR_TOKEN>"}
  }
  ```

### Create password item

- Method : ```POST```
- Request : ```http://quarkey.herokuapp.com/api/account/item/password```
- Body :

  ```json
    {
      "name"       : "Digital Ocean",
      "description": "smart cloud platform",
      "login"      : "random.user@gmail.com",
      "url"        : "https://cloud.digitalocean.com/login",
      "password"   : "motdepasse#38"
    }
  ```

### Get password item

- Method : ```GET```
- Request : ```http://quarkey.herokuapp.com/api/account/item/password```
- Return :
  
  ```json
    {
      "title": "OK",
      "description": "password list getted successful",
      "content": [
        {
          "id": "e882a1fffd624e5baa5b3e0054790af8",
          "type": "basic",
          "name": "Digital Ocean",
          "description": "smart cloud platform",
          "login": "random.user@gmail.com",
          "password": [
            "motdepasse#38",
            null
          ],
          "url": "https://cloud.digitalocean.com/login",
          "tags": [
            {
              "id": "a20cb92d0d9f43d6aef55a39909a0027",
              "name": "global",
              "color": "white"
            }
          ]
        },
        {
          "id": "6b53aaca28a6410bb8f9325acbdc26b2",
          "type": "basic",
          "name": "Steam",
          "description": "Game platform",
          "login": "nicdouille38",
          "password": [
            "motdepasse#38",
            null
          ],
          "url": "https://steampowered.com/login",
          "tags": [
            {
              "id": "acac24dff32d484fad4a65e35b49b657",
              "name": "global",
              "color": "white"
            },
            {
              "id": "5c8b07d3767b4f828701318e35b65550",
              "name": "games",
              "color": "blue"
            }
          ]
        },
        {
          "id": "b8174dd5b93a4a1c86bdb8854709e475",
          "type": "basic",
          "name": "Riot account",
          "description": "To play lol and valorant",
          "login": "nicdouille38",
          "password": [
            "motdepasse#38",
            null
          ],
          "url": "https://riot-games.com/login",
          "tags": [
            {
              "id": "3f083e9efb7a4c639977b1f9432debd7",
              "name": "global",
              "color": "white"
            },
            {
              "id": "5c8b07d3767b4f828701318e35b65550",
              "name": "games",
              "color": "blue"
            }
          ]
        }
      ]
    }
  ```

### Delete password item

- Method : ```DELETE```
- Request : ```http://quarkey.herokuapp.com/api/account/item/password```
- Parameter :
  - password_id : ```UUID password id```
- Example : ```http://quarkey.herokuapp.com/api/account/item/password?password_id=8ef944aa5b7c458d9ef9b60ab90d3e5a```

### Create tag item
> _A tag name is unique per account_

- Method : ```POST```
- Request : ```http://quarkey.herokuapp.com/api/account/item/tag```
- Body :

  ```json
  {
    "name"   : "Digital Ocean",
    "color"  : "blue" 
  }
  ```

### Get tag item
_**In development**_

- Method : ```GET```
- Request : ```http://quarkey.herokuapp.com/api/account/item/tag```

### Delete tag item

- Method : ```DELETE```
- Request : ```http://quarkey.herokuapp.com/api/account/item/tag```
- Parameter :
  - tag_id    : ```UUID```
  - tag_name  : ```TEXT```

### Link password to tag

- Method : ```POST```
- Request : ```http://quarkey.herokuapp.com/api/account/item/password/link/to/tag```
- Parameter :
  - password_id : ```UUID```
  - tag_id      : ```UUID```
  - tag_name    : ```TEXT``` _you can specify tag name instead tag id_
- Body :
  
  ```json
  {
	  "password_id": "b8174dd5-b93a-4a1c-86bd-b8854709e475",
	  "tag_id": "5c8b07d3-767b-4f82-8701-318e35b65550"
  }
  ```

### Unlink password from tag

- Method : ```DELETE```
- Request : ```http://quarkey.herokuapp.com/api/account/item/password/link/to/tag```
- Parameter :
  - password_id : ```UUID```
  - tag_id      : ```UUID```
  - tag_name    : ```TEXT``` _you can specify tag name instead tag id_
- Body : 

  ```json
  {
	  "password_id": "b8174dd5-b93a-4a1c-86bd-b8854709e475",
	  "tag_id": "5c8b07d3-767b-4f82-8701-318e35b65550"
  }
  ```

### Create tester key

- Method : ```POST```
- Request : ```http://quarkey.herokuapp.com/api/account/tester/key```

## License

This project is licensed under [MIT](https://github.com/PowerSaucisse/quarkey-api-server/blob/dev/LICENSE).
