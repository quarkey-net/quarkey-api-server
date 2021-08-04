# DEVELOPER NOTES

## API DOCUMENTATION

There is currently no domain name assigned to the service. However, a Heroku version is hosted in order to perform security tests and audits. If you wish to contribute, you can request key from the following address:
  - esteban.ristich@protonmail.com

> The API currently only supports JSON. So please define in your header the following key and value `'Content-Type': 'application/json'` and your token `'Authorization': 'YOUR_TOKEN'`. This token will be needed to access all resources, except :
> - ```http://quarkey.herokuapp.com/api/auth/register```
> - ```http://quarkey.codewire.co/api/auth/login```

### CREATE AN ACCOUNT

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

### LOGIN TO AN ACCOUNT
>_For security and caching reasons, login requests are made via the POST method._

- Method : ```POST```
- Request : ```http://quarkey.codewire.co/api/auth/login```
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

### CREATE PASSWORD ITEM

- Method : ```POST```
- Request : ```http://quarkey.codewire/api/account/item/password```
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

### GET PASSWORD ITEM

- Method : ```GET```
- Request : ```http://quarkey.codewire/api/account/item/password```
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

### DELETE PASSWORD ITEM

- Method : ```DELETE```
- Request : ```http://quarkey.codewire/api/account/item/password```
- Parameter :
  - password_id : ```UUID password id```
- Example : ```http://quarkey.codewire/api/account/item/password?password_id=8ef944aa5b7c458d9ef9b60ab90d3e5a```

### CREATE TAG ITEM
> _A tag name is unique per account_

- Method : ```POST```
- Request : ```http://quarkey.codewire/api/account/item/tag```
- Body :

  ```json
  {
    "name"   : "Digital Ocean",
    "color"  : "blue" 
  }
  ```

### GET TAG ITEM
_**In development**_

- Method : ```GET```
- Request : ```http://quarkey.codewire/api/account/item/tag```

### DELETE TAG ITEM

- Method : ```DELETE```
- Request : ```http://quarkey.codewire/api/account/item/tag```
- Parameter :
  - tag_id    : ```UUID```
  - tag_name  : ```TEXT```

### CREATE LINK PASSWORD TO TAG

- Method : ```POST```
- Request : ```http://quarkey.codewire/api/account/item/password/link/to/tag```
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

### DELETE LINK PASSWORD TO TAG

- Method : ```DELETE```
- Request : ```http://quarkey.codewire/api/account/item/password/link/to/tag```
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

### CREATE TESTER KEY

- Method : ```POST```
- Request : ```http://quarkey.codewire/api/account/tester/key```
