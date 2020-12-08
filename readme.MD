# Tor's Ticket Lobby

## Table of Contents
- General Information and Project Layout
- Notes on Packages
- Setting Up a Local Instance
- Tests


### General Information and Project Layout

This Django application contains an anonymous ticket handling system. It
allows individuals that would like to submit an anonymous ticket to Tor
to do so by receiving a pass-code of english words based on dictionary
dice rolls.

It has been structured in such a way to allow later expansion for other,
related functions and is currently divided into three apps:

1. ***/TicketLobby***: This is main app folder, in which the settings.py file 
and other base Django files are found.

2. ***/AnonTicket***: This is the folder for the anonymous ticket submission app
itself.

3. ***/Shared***: This is primarily for static files and templates that are likely
to be expanded or utilized in other parts of the project. By moving the 
base templates and static files into their own app, overall development 
and deployment are easier. (Note: This is not the recommend approach if 
you are designing a Django project with a LOT of apps.)


### Notes on Packages:

The packages in the requirements.txt file are necessary for the ticketlobby
to function (see below for installation instructions.)

Environment variables are tracked using the python-decouple package, which
increases security by moving important keys, tokens, etc. to the .env
file located in the base installation. If you're unable to perform 
manage.py runserver, make sure you have set something in the SECRET_KEY
field in the .env file, and that DEBUG is set to "True". If DEBUG is 
set to "False", you will need to make sure something is filled in for
the allowed hosts field.


### To run it locally

You need to start by setting the `SECRET_KEY` variable in the .env file.

Then run the following commands:

```
1. Make a virtual environment:
    $ python3 -m venv myvenv
2. Activate the environment:
    $ source myvenv/bin/activate
3. Install required packages:
    $ pip install -r requirements.txt
4. Make all migrations to set up database.
    $ python manage.py makemigrations
5. Migrate the database:
    $ python manage.py migrate
6. You can check or launch by using the "runserver command."
    $ python manage.py runserver
```

When `runserver` is running, you should be able to point your browser to
<http://127.0.0.1:8000/> and reach the local version of the application.


### Notes on the virtual environment

Make sure you're inside of your virtual environment when you're making
any changes! You'll know it's on, because (myvenv) will be at the 
beginning of the command line. If you ever type:
    $ python manage.py runserver

and you see something like:

> Command 'python' not found, did you mean:
>   command 'python3' from deb python3

then you may have accidentally turned your viritual environment off!

If you want to ever exit your virtual environment, just type
    $ deactivate.

### Tests

Tests currently live in the tests.py files that are automatically set up
when the apps are created (e.g., the anonticket folder has a tests.py file
specifically for functions in the anonticket app. In the future, tests
will likely be moved to a Django testing package, such as django-test-plus.

For now, you can run the tests from the command line, with:

$ python manage.py test
