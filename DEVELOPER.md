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
> **'Authorization': 'YOUR_TOKEN'**. Ce dernier vous sera utile
> pour acceder à toutes les resources, excepter : 
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

For security and caching reasons, login requests are made 
via the POST method.

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
>        "description": "login success",
>        "content": {"token": "Bearer YOUR_TOKEN"}
>    }
>    ```

### CREATE PASSWORD ITEM

- Method : ```POST```
- Request : ```http://quarkey.codewire/api/account/item/password```

### GET PASSWORD ITEMS

- Method : ```GET```
- Request : ```http://quarkey.codewire/api/v1/user/{user_id}/password_item```
- Parameter :
  - user_id : ```uuid v4```
- Header :

>    ```json
>    {
>        "Content-Type": "application/json",
>        "Authorization": "YOUR_TOKEN"
>    }
>    ```
