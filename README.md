# juniordev

## Runing localy

### Dependencies
To run this repo you will need:
1. Python 3.6 or later
2. pip
3. `pip install -r requirements.txt`

### Recomendations
1. Make a virtual enviroment for python
2. Have a postgres(first load will be faster)
* You will also need to change some settings in the [./juniordev/settings.py](./juniordev/settings.py) file in the DATABASES varible, around line 80.
Like the name, user, password, host (if you are not hosting it localy the db), and port (If you are using some other port for the db)
```
'name': name_of_the_db,
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
`python manage.py runserver 127.0.0.1:A_port_that_is_not_in_use_example 8005`


### Run after changes
If you make changes to the models file you will need to run to get them writen to the database
```
python manage.py makemigrations
python manage.py migrate
```

## Deploying
### Recomendations
Export to os enviroment a SECRET_KEY == "A random string" and DEBUG_VALUE == 'False'

### Command to deploy it
```
python manage.py collectstatic
python manage.py runserver 0.0.0.0: The_port_you_want_it_to_run_on
```