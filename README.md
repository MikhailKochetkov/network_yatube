# yatube_project
### Description
Social network of bloggers 
### Technology
Python 3.9

Django 3.2
### Running a project in dev mode
- Install and activate the virtual environment 

```
python -m venv env
```

```
source env/bin/activate
```

- Install dependencies from requirements.txt file

```
pip install -r requirements.txt
```

- In the folder with the manage.py file, run the command:

```
python manage.py runserver
```

### Project API Documentation:

The list of requests to the resource can be found in the API description

```
http://127.0.0.1:8000/redoc/
```

Request examples
 - /api/v1/posts/ (GET) - Get a list of all posts.
 - /api/v1/posts/ (POST) - Adding a new post.
 - /api/v1/posts/{id}/ (PUT) - Editing a post.

### Author
Mikhail Kochetkov
