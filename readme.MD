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

## 1.0: General Information and Project Layout, Including Quickstart Notes For Admins:

Django applications or projects generally contain a main project folder 
(in this case 'ticketlobby'), as well as several app folders, which can be
'turned on' and 'turned off' by their inclusion in the main project folder's
settings.py file.

This project has been structured in such a way to maximize the potential
for later development and expansion. It is currently divided into three 
main folders:

1. ***/TicketLobby***: This is main project folder, in which the settings.py file 
and other base Django files are found.

2. ***/AnonTicket***: This is the folder for the AnonTicket app.

3. ***/Shared***: This is a pseudo-app, primarily for static files and 
templates likely to be expanded or utilized in other parts of the project.

### Adding Projects

Once an admin has created a superuser, adding a project to the database
is extremely simple, in that it requires only one piece of information--
the gitlab id number of the project (available on the project's gitlab
page. (From the admin panel, click "projects" - > "create" - > and type in the
gitlab id number. Hit save.)

Django will then create a gitlab object instance and fetch all the project's 
details for the database entry and save them. It will also check the GLGroup's to
see if a matching gitlab group already exists in the database; if it does 
not, it will fetch the group's information from gitlab, create the group, and 
assign the project to the relevant gitlab group.

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

### Notes on Moderators Group:

Once the project has been installed and migrations applied, it is 
recommended to run create_groups for ease of admin administration.

/anonticket/management/commands has a file in it, "create_groups.py", 
which will automatically create two groups, "Moderators" and "Account
Approvers", when run from the command line with:

$ python manage.py create_groups

The "Moderators" will automatically have the following permissions assigned:
- View User Identifier
- View Git Lab Group
- View Project
- Add/Delete/Change/View Issue
- Add/Delete/Change/View Note

The "Acount Approvers" will automatically have the following permissions assigned:
- View User Identifier
- Add/Delete/Change/View Gitlab Account Request

Once create_groups.py is run, users can be created by a super_user via
the admin panel. make sure to:
1. Assign "staff" status to moderators and account approvers so that
they are able to login.
2. Assign the group "Moderators" to users that will be editing notes
and issues.
3. Assign the group "Account Approvers" to users that will be approving
Gitlab Account Requests (this functionality has not yet been added to the
portal but should be coming at a future date.)
4. Note: Users can be in more than one group.

If, in the future, you wish to update the permissions for the group, you
can do so via the admin panel, but it's recommended to update the file
in anonticket/management/commands/create_groups.py instead, as this 
will ensure consistency at a later date.

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
7. Create the superuser
    $ python manage.py createsuperuser
    (follow the prompts):
8. Create groups "Moderators" and "Account Approvers"(see explanation above):
    $ python manage.py create_groups
9. Add gitlab tokens and other variables in the .env file.

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
other dictionaries, but a Mixin has been created (PassUserIdentifierMixin) that has been
used to create all of the class based views. This Mixin will automatically pass
the user_identifier from the url argument to a context dictionary called "results"
to minimize code duplication when repurposing templates across function and class
based views.

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

Additionally, views can leverage decorators like @validate_user, which
wraps the view in a function that determines if the user_identifier codephrase in the 
URL path meets validation requirements; if not, it redirects the user to an invalid
user_identifier view.

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
specifically for functions in the anonticket app.)

Coverage is verified through a variety of tools, including coverage.py
[https://coverage.readthedocs.io/en/latest/]. Coverage includes a C 
extension for speed (that is also required to execute some functions.) 
Once requirements have all installed from requirements.txt, you can 
verify the C extension is installed correctly with 

$ coverage --version

which should return "with C extension" or "without C extension".
[https://coverage.readthedocs.io/en/latest/install.html]

Testing sets up a test_database and should not interact with the project's
actual database.

1. To run tests from the command line without coverage:

$ python manage.py test

2. If you would like a more verbose output from testing (e.g, with test_names),
you can add -v1, -v2, or -v3 as an argument:

$ python manage.py test -v2

3. To run tests with coverage (using Python-Coverage package):

$ coverage erase
$ coverage run manage.py test
$ coverage report

4. After running coverage run, the coverage data is stored in the .coverage file. 
Run this command to generate an HTML report from this file:

$ coverage html

This creates a folder called htmlcov. Open up htmlcov/index.html and you'll
see an easier to parse version of the report.

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
