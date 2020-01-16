# juniordev

## Runing localy

### Dependencies
To run this repo you will need:
1. Python 3.6 or later
2. Django (`pip install django`)

### Recomendations
1. Make a virtual enviroment for python
2. Have a postgres(first load will be faster)
* For the the django project to work with postgress make sure `psycopg2` is installed with pip
* You will also need to change some settings in the [./juniordev/settings.py](./juniordev/settings.py)file under the DATABASES varible around line 80
Like the name, user, password, host(if you are not hosting it localy), and port (If you are using some other port for the database)
```
'name': name_of_the_databases,
'user': username_for_the_user,
'password': password_for_the_user,
```

### First time
This will create all of the tabels in the database
```
python manage.py migrate
python manage.py runserver
```
(127.0.0.1:8000) the server will run on port 8000 if it's not in use then it will give you an error and you will need to run
`python manage.py runserver 127.0.0.1:A port that is not in use example 8005`


### Run after changes
If you make changes to the models file you will need to run to get them writen to the database
```
python manage.py makemigrations
python manage.py migrate
```

## Deploying
### Recomendations
Export to os enviroment a SECRET_KEY == "A random string" and DEBUG_VALUE == 'False'


```
python manage.py collectstatic
python manage.py runserver 0.0.0.0: The port you want it to run on
```