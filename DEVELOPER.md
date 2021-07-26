# DEVELOPER NOTES

## API PRIVATE DOCUMMENTATION

L'api est actuellement en version de dévelopement, il n'existe donc pas actuellement
de nom de domaine attribué au service. Or l'api à terme utilisera le nom de domaine
de **ColdWire**.

> L'API supporte actuellement seulement **JSON** ('Content-Type: application/json').
> Elle pourra propablement integrer **MsgPack** dans ses futures versions.

### REGISTER

- Method : ```POST```
- Request : ```http://quarkey.codewire.co/api/v1/register```
- Parameter : **none**
- Body :

>    ```json
>    {
>        "username": "Esteban",
>        "email": "esteban.ristich@protonmail.com",
>        "password": "motdepasse#38"
>    }
>    ```

- Return :

>    ```json
>    {
>        "title": "REGISTER_SUCCESS",
>        "description": "Register successful! Please verify your email address",
>    }
>    ```

### LOGIN

- Method : ```POST```
- Request : ```http://quarkey.codewire.co/api/v1/login```
- Parameter : **none**
- Body :

>    ```json
>    {
>        "username": "Esteban",
>        "password": "motdepasse#38"
>    }
>    ```

- Return :

>    ```json
>    {
>        "title": "LOGIN_SUCCESS",
>        "description": "Login successful!",
>        "token": "Bearer YOUR_TOKEN"
>    }
>    ```

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
