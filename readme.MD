# Tor's Ticket Lobby

## Table of Contents
1: General Information and Project Layout

2: Getting Started: 
- Notes on Packages
- Setting Up a Local Instance
- Notes on Virtual Environment

3: Django In A Nutshell:
- Templates
- Models
- Views
- URLs
- Tests

4:  GitLab Python
---

## 1.0: General Information and Project Layout

Django applications or projects generally contain a main project folder 
(in this case 'ticketlobby'), as well as several app folders, which can be
'turned on' and 'turned off' by their inclusion in the main project folder's
settings.py file.

This Django application contains a specific app, 'anonticket', which 
is an anonymous ticket handling system to allow anonymous submission of an 
issue to TorProject's GitLab lobby via creation of User Identifier 
code-phrases based on dice rolls from a dictionary of english words.

This project has been structured in such a way to allow later expansion for other,
related functions and is currently divided into three main folders:

1. ***/TicketLobby***: This is main project folder, in which the settings.py file 
and other base Django files are found.

2. ***/AnonTicket***: This is the folder for the anonymous ticket submission app
itself.

3. ***/Shared***: This is a pseudo-app, primarily for static files and templates 
likely to be expanded or utilized in other parts of the project. By moving the 
base templates and static files into their own app, overall development 
and deployment are easier. (Note: This is not the recommend approach if 
you are designing a Django project with a LOT of apps.)

---

## 2.0 Getting Started: 
### Notes on Packages:

The packages in the requirements.txt file are necessary for the ticketlobby
to function (see below for installation instructions, or 'packages' below
for more information on specific packages.)

Environment variables are tracked using the python-decouple package, which
increases security by moving important keys, tokens, etc. to the .env
file located in the base folder. If you're unable to perform 
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

---
## 3.0 Django (and this project) in A Nutshell:

When a user navigates to an URL associated with this project, Django matches the 
URL to the appropriate pattern in urls.py. It strips any needed arguments from the URL based on 
the logic in urls.py, and, based on urls.py, determines which VIEW to use. The 
view itself may contain logic, including what to do with any arguments from the URL, how 
to handle forms, GET vs POST requests, when to communicate with the database, etc. 

Once those steps are carried out, the view generally instructs Django to initiate a redirect
to another view, or to render an html page using one or more html TEMPLATES. Arguments for
rendering the html template are usually passed to the template as a dictionary (associative array),
and can be called by the template (e.g., if the dictionary is passed as {results}, {{results.user_identifier}} 
is equivalent to results['user_identifier'].) Context dictionaries can contain strings, lists, or 
other dictionaries.

### Templates

Templates specific to the anonticket portion of this project are in anonticket/templates/anonticket.
The repetition of anonticket above is Django's recommend method for namespacing; as Django will
search for templates within *any* app folder called 'templates', this name-spacing prevents confusion.

Additionally, there is a folder called 'templates' in 'shared'; here, 'shared' is 
a pseudo-app that contains files that will be used across various apps in this project. The
overall layout template, including side-bar menu, is here, as well as the css files, fonts,
and other static files (like images.) The CSS is based on Tor Project's style-guide 
(styleguide.torproject.com), which uses bootstrap templates for layout.

### Models

The models for database objects are in anonticket/models.py.

### Views

The 'engine' that drives this project is primarily contained in anonticket/views.py. 
At current, this project uses a mixture of class-based views and function-based views.
Each view is explained with a doc-string and has comments throughout to explain specific
functions from within the view.

If a view relies heavily on a form, processing for that view may have been moved to forms.py.

### URL-Pathing

The main URL structures at this time are located in anonticket/urls.py (and all of 
these URLs are included in the main URLS.py located at ticketlobby/urls.py) Values that
contain arguments like <str:identifier> pass that argument as an arg/kwarg to be used by the 
associated view. 

User Identifier code-phrases are not saved to the database until they have been used
to perform an action, such as create a ticket. As such, there are validation functions
in the views which take arguments from the URL as noted above.

### Tests

Tests currently live in the tests.py files that are automatically set up
when the apps are created (e.g., the anonticket folder has a tests.py file
specifically for functions in the anonticket app.) In addition, 

Testing sets up a test_database and should not interact with the project's
actual database.

For now, you can run the tests from the command line, with:

$ python manage.py test

If you would like a more verbose output from testing (e.g, with test_names),
you can add -v# as an argument:

$ python manage.py test -v2

## Packages

### Python-Gitlab

The anonticket app uses the Python-Gitlab package to communicate with 
the GitLab API.

Some sample reference files to demonstrate dictionaries returned by 
get queries, including pretty-printed issue and note dictionaries, 
are available in shared/reference_files.

### Django-Markdownify

Python-Django package that allows you to use a 'markdownify' filter 
to render markdown as html, including safe functions. Automatically
installs Markdown and Bleach dependencies. 

To run, markdownify is added as an app in ticketlobby/settings.py 
(and can be disabled by removing that line.)

To load into a template, use the {% loadmarkdownify %} template tag.
Add '|markdownify|' as a filter where you want markdown rendered as 
html.

Documentation here: https://django-markdownify.readthedocs.io/en/latest/index.html
