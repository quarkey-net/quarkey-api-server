# QuarKEY-api-server

![Quarkey logo](https://github.com/PowerSaucisse/quarkey-api-server/blob/main/assets/img/quarkey-full.png?raw=true) [![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/PowerSaucisse/Quarkey-api-server) [![Chat](https://img.shields.io/badge/chat-on%20discord-7289da.svg)](https://discord.gg/PatReunPk5)

REST API Backend for QuarKEY Frontend

Une api "RESTful" pour le gestionnaire de mot de passe Quarkey
et son application Web faite en VueJS. Elle supportera à terme
dans sa version stable le chiffrement expérimental quantique.

> Si vous souhaitez utiliser l'API en version de développement 
> publique vous devrez alors demander une clé de développement 
> pour activer votre compte à l'adresse : **esteban.ristich@protonmail.com** 
> ou alors une notification sur notre discord.

## Quickstart

L'API peut-être construite en local. Pour une configuration 
précise de l'api lors de son lancement, veuillez vous référer 
au fichier **utils/configs.py**

> L'API requiert un serveur **postgresql**. Les tables à charger
> sont spécifier dans le dossier **database/sql** et doivent
> êtres chargé dans cet ordre :
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
