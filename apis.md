


```bash
curl --location --request GET 'http://127.0.0.1:8000/auth/users/me' \
--header 'Authorization: Token 1816848305f547cfc095930d396310fc2be16cf3' \
--header 'Content-Type: text/plain' \
--data-binary '@'

curl --location --request POST 'http://127.0.0.1:8000/auth/token/login/' \
--header 'Content-Type: application/json' \
--data-raw '{
    "username": "admin",
    "password": "1"
}'
```
