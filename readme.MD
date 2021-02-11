# Anon-Ticket: Anonymous Gitlab Reporting for Tor

A web application that allows web users to create
anonymous tickets on the Tor Browser's Gitlab instance by leveraging
the GitLab API (Python-Gitlab package.)<br>
<br>
***
## 1.0 Quickstart:
Clone the repo. Rename the env_sample.txt file to just “.env”. Open it
and delete first line that says "delete me", then set the SECRET_KEY to a string of 
your choosing. 

This project uses Django-Ratelimit.

Set the LIMIT_RATE value to determine how many form post requests
to allow per time unit, or choose '0/s' to block all requests or leave as 'None'
to allow all requests. Change the value of MAIN_RATE_GROUP to a group name
of your choosing, or you can leave blank to have views limit individually.

Run the following commands:

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
7. Create a superuser
    $ python manage.py createsuperuser
    (follow the prompts)
8. Create groups "Moderators" and "Account Approvers"(see explanation above):
    $ python manage.py create_groups
9. Add gitlab tokens and other variables in the .env file.
```
When `runserver` is running, you should be able to point your browser to
<http://127.0.0.1:8000/> and reach the local version of the application.<br>
<br>
***
## Table of Contents:

1. Quickstart (above)
2. Notes for Admins
    - 2.1 Fast Project Add From Gitlab
    - 2.2 Programmatic Groups and Permissions
    - 2.3 Adding Moderators and Account Approvers
3. Project Structure and Function:
    - 3.1 Folder Layout
    - 3.2 Anon-Ticket Request-Response in a Nutshell
    - 3.3 Models
    - 3.4 Views
    - 3.5 URL Pathing
    - 3.6 Templates
4. Packages
5. Tests

***

## 2.0 Notes for Admins

***

### 2.1 Fast Project Add from GitLab	
In order to use Anon-Ticket to receive issues, notes, and gitlab account 
requests, a project has to be first be added to the database by a 
superuser via the admin panel. The only piece of information needed to 
do this is the ***project’s Gitlab ID number***, available on that 
project’s gitlab page. Once the number is filled in and the project is 
saved, Anon-Ticket will ***automatically fetch*** all necessary project 
information from the GitLab API, including the group, title, description, 
web_urls, etc.

Anon-Ticket will also check the GitLabGroup objects to see if a
matching group already exists in the database; if not, Anon-Ticket will
***automatically create*** the GitlabGroup object, including fetching 
the information from Gitlab, creating the group, and assigning the
project to the relevant group.
<br>

### 2.2 Programmatic Groups and Permissions:

Once the project has been installed and migrations applied, Moderator
and Account Approvers can be created from the command line:

$ python manage.py create_groups

Anon-Ticket will automatically create two groups, "Moderators" and 
"Account Approvers", and assign the permissions defined in the dictionaries
in /anonticket/management/commands/create_groups.py. These permissions 
can be changed by changing this file. These Group names are important; 
they are used during the authentication process for Moderator and 
Account-Approver specific views.

The "Moderators" will automatically have the following permissions assigned:
- View User Identifier
- View Git Lab Group
- View Project
- Add/Delete/Change/View Issue
- Add/Delete/Change/View Note

The "Account Approvers" will automatically have the following permissions assigned:
- View User Identifier
- Add/Delete/Change/View Gitlab Account Request

If, in the future, you wish to update the permissions for the group, you
can do so via the admin panel, but it's recommended to update the file
in anonticket/management/commands/create_groups.py and then rerun 
“python manage.py create_groups”  instead, as this will ensure 
consistency at a later date. All users assigned to a group will have
their permissions updated.

### 2.3 Adding Moderators and Account Approvers (Users):

1. Create the user in the admin panel - only username and email are 
necessary.
2. Assign "staff" status; without "staff", the user will not be able to
log into the system to perform moderation tasks.
3. Assign the group "Moderators" to users that will be editing notes
and issues.
4. Assign the group "Account Approvers" to users that will be approving
Gitlab Account Requests (this functionality has not yet been added to
Anon-Ticket, but should be coming at a future date.)
5. Note: Users can be in more than one group.

<br>

***

## 3.0 Project Structure and Function

***

### 3.1 Folder Structure:
Django applications or projects generally contain a main project folder 
(in this case 'ticketlobby'), as well as several app folders. Apps can 
be turned “on” or “off” by changing the allowed_apps setting in  
/ticketlobby/settings.py.

This project has been structured in such a way to maximize the potential
for later development and expansion. It is currently divided into three 
main folders:

1. ***/TicketLobby***: The main project folder, in which most 
configuration files are found.

2. ***/AnonTicket***: The folder for the AnonTicket app.

3. ***/Shared***: This is a pseudo-app, primarily for static files and 
templates likely to be expanded or utilized in other parts of the project.

### 3.2 Anon-Ticket Request-Response in a Nutshell 

When a user navigates to an URL associated with this project, 
Django matches the URL to the appropriate pattern in urls.py. It strips 
any needed arguments from the URL based on the logic in urls.py, and, 
based on urls.py, determines which VIEW to use. The view itself may 
contain logic, including what to do with any arguments from the URL, how 
to handle forms, GET vs POST requests, when to communicate with the database, etc. 

Once those steps are carried out, the view generally instructs Django to 
return a redirect to another view, or to render an html page using one 
or more html TEMPLATES. Arguments for rendering the html template are 
usually passed to the template context as a dictionary (associative array),
and can be called by the template (e.g., if the dictionary is passed as 
{results}, a {{results.user_identifier}} call in the template is equivalent to 
results['user_identifier'].) Context dictionaries can contain strings, lists, or 
other dictionaries.

In order to increase privacy for end users, who may wish to be anonymous,
users do not authenticate via a standard username/password cookie method. 
Instead, once a User Identifier code-phrase is created, it is passed 
to views via an arg/kwarg from the URL path, e.g., </user/<str:identifier>,
into a dictionary called "results". In order to create consistency between
class based views (CBV's) and function-based views (FBV's), both of which
are utilized in this project, a Mixin has been created called
PassUserIdentifierMixin, which passed the user_identifier kwarg (if it
exists) from the URL to the CBV's context dictionary inside of another 
dictionary called "results". This minimzes code duplication across 
views and allows developers to repurpose the same template for CBVs and
FBVs.

### 3.3 Models

The models for database objects are in anonticket/models.py.

### 3.4 Views

The 'engine' that drives this project is primarily contained in anonticket/views.py. 
At current, this project uses a mixture of class-based views and function-based views.
Each view is explained with a doc-string and has comments throughout to explain specific
functions from within the view.

If a view relies heavily on a form, processing for that view may have been moved to forms.py.

Additionally, views can leverage decorators like @validate_user, which
wraps the view in a function that determines if the user_identifier codephrase in the 
URL path meets validation requirements; if not, it redirects the user to an invalid
user_identifier view.

### 3.5 URL-Pathing

The main URL structures at this time are located in anonticket/urls.py (and all of 
these URLs are included in the main URLS.py located at ticketlobby/urls.py) Values that
contain arguments like <str:identifier> pass that argument as an arg/kwarg to be used by the 
associated view. 

User Identifier code-phrases are not saved to the database until they have been used
to perform an action, such as create a ticket. As such, there are validation functions
in the views which take arguments from the URL as noted above.

### 3.6 Templates

Templates specific to the anonticket portion of this project are in anonticket/templates/anonticket.
The repetition of anonticket above is Django's recommend method for namespacing; as Django will
search for templates within *any* app folder called 'templates', this name-spacing prevents confusion.

Additionally, there is a folder called 'templates' in 'shared'; here, 'shared' is 
a pseudo-app that contains files that will be used across various apps in this project. The
overall layout template, including side-bar menu, is here, as well as the css files, fonts,
and other static files (like images.) The CSS is based on Tor Project's style-guide 
(styleguide.torproject.com), which uses bootstrap templates for layout.

## 4.0 Packages

### Notes on Packages:

The packages in the requirements.txt file are necessary for the ticketlobby
to function.

Environment variables are tracked using the python-decouple package, which
increases security by moving important keys, tokens, etc. to the .env
file located in the base folder. If you're unable to perform 
manage.py runserver, make sure you have set something in the SECRET_KEY
field in the .env file, and that DEBUG is set to "True". If DEBUG is 
set to "False", you will need to make sure something is filled in for
the ALLOWED_HOSTS field.

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

### Python-Coverage
(See "Tests", below.)

### 5.0 Tests

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



