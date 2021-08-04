# DEVELOPER NOTES

## API DOCUMENTATION

Il n'existe pas actuellement de nom de domaine attribué au service.
Cependant une version **Heroku** est hébergé afin d'effectuer des 
tests et audits de sécurité. Si vous souhaitez contribuer, vous
pouvez demander des clés à l'une des adresses suivantes :
  - esteban.ristich@protonmail.com
  - regis.brasme@gmail.com

> L'API supporte actuellement seulement **JSON**. Veuillez 
> donc définir dans votre header la clé et la valeur suivante 
> **'Content-Type': 'application/json'** ainsi que votre token 
> **'Authorization': 'YOUR_TOKEN'**. Ce dernier vous sera 
> nécessaire pour acceder à toutes les resources, excepter : 
> - ```http://quarkey.herokuapp.com/api/auth/register```
> - ```http://quarkey.codewire.co/api/auth/login```

### CREATE AN ACCOUNT

- Method : ```POST```
- Request : ```http://quarkey.herokuapp.com/api/auth/register```
- Body :

>    ```json
>    {
>        "username" : "esteban",
>        "firstname": "Esteban",
>        "lastname" : "Ristich",
>        "email"    : "esteban.ristich@protonmail.com",
>        "password" : "motdepasse#38",
>        "key"      : "B14FDA9A9D9363FA4E8F" # past your tester key
>    }
>    ```

- Return :

>    ```json
>    {
>        "title": "CREATED",
>        "description": "Register successful!",
>    }
>    ```

### LOGIN TO AN ACCOUNT

_For security and caching reasons, login requests are made 
via the POST method._

- Method : ```POST```
- Request : ```http://quarkey.codewire.co/api/auth/login```
- Body :

>    ```json
>    {
>        "username": "esteban",
>        "password": "motdepasse#38"
>        // You can also use "email" json key instead of "username" to login with your email adress
>    }
>    ```

- Return :

>    ```json
>    {
>        "title": "OK",
>        "description": "success to login",
>        "content": {"token": "Bearer YOUR_TOKEN"}
>    }
>    ```

### CREATE PASSWORD ITEM

- Method : ```POST```
- Request : ```http://quarkey.codewire/api/account/item/password```
- Body :

>    ```json
>    {
>        "name"       : "Digital Ocean",
>        "description": "smart cloud platform",
>        "login"      : "random.user@gmail.com",
>        "url"        : "https://cloud.digitalocean.com/login",
>        "password"   : "motdepasse#38"
>    }
>    ```

- Return :

>    ```json
>    {
>        "title": "CREATED",
>        "description": "resource created successful"
>    }
>    ```

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

### CREATE TAG ITEM

_A tag name is unique per account_

- Method : ```POST```
- Request : ```http://quarkey.codewire/api/account/item/tag```
- Body :

>    ```json
>    {
>        "name"   : "Digital Ocean",
>        "color"  : "blue" 
>    }
>    ```

### GET TAG ITEM

_**In development**_

- Method : ```GET```
- Request : ```http://quarkey.codewire/api/account/item/tag```

### DELETE TAG ITEM

- Method : ```DELETE```
- Request : ```http://quarkey.codewire/api/account/item/tag```
- Parameter :
  - tag_id    : ```UUID tag id```
  - tag_name  : ```TEXT tag name```

### CREATE LINK PASSWORD TO TAG

- Method : ```GET```
- Request : ```http://quarkey.codewire/api/account/item/{password_id}/link/to/tag/{tag_id}```
- Request : ```http://quarkey.codewire/api/account/item/{password_id}/link/to/tag/{tag_name}```
- Parameter :
  - password_id : ```UUID password id```
  - tag_id      : ```UUID tag id you want to link to password```
  - tag_name    : ```TEXT tag name you want to link to password```

### DELETE LINK PASSWORD TO TAG

- Method : ```DELETE```
- Request : ```http://quarkey.codewire/api/account/item/{password_id}/link/to/tag/{tag_id}```
- Request : ```http://quarkey.codewire/api/account/item/{password_id}/link/to/tag/{tag_name}```
- Parameter :
  - password_id : ```UUID password id```
  - tag_id      : ```UUID tag id you want to link to password```
  - tag_name    : ```TEXT tag name you want to link to password```