# Anon-Ticket: Anonymous Gitlab Reporting for Tor

A web application that allows users to create
anonymous tickets on the Tor Browser's GitLab instance by leveraging
the GitLab API (Python-Gitlab package). Created as an
[Outreachy](https://www.outreachy.org/) winter of 2021 internship project
by [Maria Violante](https://mviolante.com), who is also the 
current maintainer.

For bug reports and feature requests, please consider submitting an 
anonymous ticket ... to Anon-Ticket ... via [Anon-Ticket](https://anonticket.onionize.space/)! ;)
<br>

***

## Table of Contents:

1. Intro and Setup
    - 1.1 Quickstart
    - 1.2 Project Aim and Use

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
    - 4.1 General notes
    - 4.2 Python-Decouple
    - 4.3 Python-Gitlab
    - 4.4 Django-Markdownify
    - 4.5 Django-Ratelimit
    - 4.6 Django-Test-Plus
    - 4.7 Python Coverage

5. Tests
    - 5.0 Running Tests
    - 5.1 Tagged Tests
    - 5.2 Run with Coverage

***

## 1.0 Intro

***

### 1.1 QuickStart

***
SETTINGS:

1.  Clone the repo from a fork.
2.  Rename the env_sample.txt file to just “.env”. 
3.  Open it and delete first line.
4.  Set the secret key to one of your choosing.
5.  Set GITLAB_SECRET_TOKEN as your Tor GitLab account token.
6.  If you have the ability to make user accounts, you can set the
    GITLAB_ACCOUNTS_SECRET_TOKEN variable.
7.  Set the GITLAB_TIMEOUT to a number of seconds.
8.  Enter a value in MAIN_RATE_GROUP - can be any string of your choosing.
9.  Enter a value in LIMIT_RATE using an integer, a slash, and a unit of
    time for the denominator, e.g., 1/s, 10/m, 100/hr, etc.
10. BLOCK_ALL should be left as false, setting as True will block all
    POST requests from forms in Anon-Ticket.
11. If running on a server, add an extra host in ALLOWED_HOSTS.

INSTALLATION:

Run the following commands:

```
1. Make a virtual environment:
    $ python3 -m venv myvenv
2. Activate the environment:
    $ source myvenv/bin/activate
3. Install required packages:
    $ pip install -r requirements.txt
4. If you have not set up your .env file, do it now, as you will need some of these
    settings in place to make migrations or runserver.
5. Make all migrations to set up database.
    $ python manage.py makemigrations
    (It may say nonothing to migrate, this is fine.)
6. Migrate the database:
    $ python manage.py migrate
7. You can check or launch by using the "runserver command."
    $ python manage.py runserver
8. Stop runserver and create a superuser
    $ python manage.py createsuperuser
    (follow the prompts)
9. Create groups "Moderators" and "Account Approvers"(see explanation above):
    $ python manage.py create_groups

```
When `runserver` is running, you should be able to point your browser to
<http://127.0.0.1:8000/> and reach the local version of the application.

*** 

### 1.2 Project Aim and Use

***

Anon-Ticket is Django/Bootstrap web portal designed to allow anonymous
users to submit tickets to supported GitLab repos without signing up
for an account with GitLab.

Users do not interact with the system via a username/password or
email combination. Instead, when they first arrive at the home screen,
they have the option to create a new user identifier, which is a
code phrase made via random dice rolls from the EFF's New Wordslist 
for Random Passphrases.

Once a user identifier has been created, and the user has chosen to log
in with the identifier, they are taken to a landing page specific to 
their user identifier, which is passed forward through the system at 
each step as a kwarg in the URL path. Each time a new page is loaded 
or an object is created, the user identifier prhase is checked by a 
validator.

From the landing page, the user has the optiont to view supported
repos and their issues/notes, search for a specific issue, or create
a new issue or note of their own. 

Once an object is created by the user, it's held in a pending status
for a moderator. The moderator view displays multiple simultaneous 
formsets demonstrating all pending issues, notes, and (coming soon!)
GitLab account reqquests that the moderator has permissions to view.
(To that end, there are two different groups of moderator permissions:
"moderator", which can see/approve pending issues and notes, and 
"account approvers", which can see/approve pending GitlLab account
requests. A moderator can belong to either or both groups.) Moderators
also have the option to edit a submitted ticket or write a comment
on a ticket for other moderators.

The final major view is a customized admin panel for the superuser, 
which includes display filters for items by status, e.g., "all pending
issues", as well as the ability to add projects to the repo with only 
the project's GitLab ID. Once the ID is filled in and the project is 
saved, the rest of the project details automatically populate from GitLab.
These features are described in greater detail below in section 2.0:
Notes for admins.

<br>

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
for later development and expansion. It is currently divided into four 
main folders:

1. ***/ticketlobby***: The main project folder, which includes the
settings.py file.

2. ***/anonticket***: The folder for the AnonTicket app.

3. ***/shared***: This is a pseudo-app, primarily for static files and 
templates likely to be expanded or utilized in other parts of the project.
It also includes custom template tags, filters, and middleware.

4. ***/gl_bot***: This folder contains the python file and tests for 
GitLabDownObject, a mock python-gitlab gitlab.GitLab object, which is 
instantiated in case of a timeout error from GitLab. Instead of having
affected views reroute to a "GitLab is down right now" page, the 
GitLabDownObject returns a mock project and issue detailing the problem
while allowing the view to render normally.

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

The models for database objects are in anonticket/models.py, with the exception of
the GitLabDownObject, which is in gl_bot/gitlabdown.py. Additionally, the models for
most of the forms are in anonticket/forms.py

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

***

## 4.0 Packages

***

### 4.1 Notes on Packages:

The packages in the requirements.txt file are necessary for the ticketlobby
to function.

Environment variables are tracked using the python-decouple package, which
increases security by moving important keys, tokens, etc. to the .env
file located in the base folder. If you're unable to perform 
manage.py runserver, make sure you have set something in the SECRET_KEY
field in the .env file, and that DEBUG is set to "True" in the .env. 
If DEBUG is False, you will need to make sure something is filled in for
the ALLOWED_HOSTS field.

### 4.2 Python-Decouple

This package is used to easily extract settings from the .env file.
Settings are called with a config() function, e.g., 
my_key = config(MY_KEY) would pull the line MY_KEY = (value) from the
.env file and assign it to the variable my_key. 

By default, all values pulled from python-decouple are strings; in those
instances where another data type (such as boolean, int, etc) are needed,
call the variable with the "cast" parameter, e.g:
my_key = config(MY_KEY, cast=bool).

More information available at: [https://github.com/henriquebastos/python-decouple/]

### 4.3 Python-GitLab

The anonticket app uses the Python-Gitlab package to communicate with 
the GitLab API. If GitLab is down, anonticket will instantiate a 
mock python-gitlab object from gl_bot/gitlabdown.py that takes 
the same calls as the python-gitlab object, but will instead 
return a message stating that GitLab appears down.

The dictionary that describes an object (issue, note, etc) is
usually returned by getting object.attributes from python-gitlab,
e.g., my_issue = my_gitlab_object.issues.get(issue_iid), dict = 
my_issue.attributes.

Some sample pretty-printed reference files to demonstrate dictionaries 
returned by get queries, including project, isssue and note dictionaries, 
are available in shared/reference_files.

Documentation at: [https://python-gitlab.readthedocs.io/en/stable/]

### 4.4 Django-Markdownify

Python-Django package that allows you to use a 'markdownify' filter 
to render markdown as html, including safe functions. Automatically
installs Markdown and Bleach dependencies. 

To run, markdownify is added as an app in ticketlobby/settings.py 
(and can be disabled by removing that line.)

To load into a template, use the {% loadmarkdownify %} template tag.
Add '|markdownify|' as a filter where you want markdown rendered as 
html.

Documentation here: [https://django-markdownify.readthedocs.io/en/latest/index.html]

### 4.5 Django-Ratelimit

Anon-Ticket uses the Django-Ratelimit package. Two custom decorators 
have been written for Anon-Ticket, expanding on the standard ip and 
key decorators included with the package: @custom_ratelimit_ip, 
and @custom_ratelimit_post. These custom decorators default to settings 
specified in the settings.py file, as well as taking a callable function, 
"get_rate_limit()", which pulls the desired limit-rate out of the .env file. 
If BLOCK_ALL is set to "True" in the .env file, all POST functions on 
decorated views will immediately be disabled, protecting the site 
in the event of an attack.

Additionally, a custom MiddleWare has been included in shared.middleware 
to faciliate rate-limiting with a reverse-proxy enabled.

### 4.6 Django-Test-Plus

Several of the tests use DjangoTestPlus, which adds extra functions to
TestCase, allowing for easier url/view/integration tests. Tests that 
do not utilize Django-Test-Plus are slowly being rewritten to 
incorporate it due to the ease of use.

More information is available here: 
[https://django-test-plus.readthedocs.io/en/latest/]

### 4.7 Python-Coverage

Test coverage tends to hover around 94 percent as measured by 
python-coverage. More information about python-coverage is available
below in 5.0: Tests. Docs for python-coverage are also available 
at [https://coverage.readthedocs.io/en/coverage-5.4/].

***

## 5.0 Tests

***

### 5.1 Running Tests

There are multiple tests.py files containing tests, including 
anonticket/tests.py and gl_bot/tests.py. All tests can be run
at once from the command line via $ python manage.py test.

1. To run tests from the command line without coverage:

$ python manage.py test

Note that during the running of the tests, the console will likely
raise several exceptions; these can be disregarded as long as the 
test itself passes. For example, rate-limit tests are designed to
raise a 403 error to ensure the rate-limiting is applied correctly.

2. If you would like a more verbose output from testing (e.g, with test_names),
you can add -v1, -v2, or -v3 as an argument:

$ python manage.py test -v2

3. Note that several of the tests have a tearDown method that 
includes clearing the cache; this is necessary as the test battery includes
tests designed to exceed the limit-rate, which provokes a 403 forbidden response. 

### 5.2 Tagged Tests

Many of the tests are also tagged using the @tag decorator. So, for 
example, anonticket/tests.py has multiple test classes tagged with 
@tag('shared-non-gitlab'), like class TestUserIdentifierInDatabase(TestCase).

To just run tests associated with a particular tag, use --tag:

$ python manage.py test --tag shared-non-gitlab

Note that if the terminal reports 0 tests run in 0.00 seconds, there 
is likely an error in one of the tests. To diagnose the error, just
run the normal test suite ($ python manage.py test)

### 5.3 Run With Python-Coverage

Coverage is verified through python coverage.
[https://coverage.readthedocs.io/en/latest/]. Coverage includes a C 
extension for speed (that is also required to execute some functions.) 
Once requirements have all installed from requirements.txt, you can 
verify the C extension is installed correctly with 

$ coverage --version

which should return "with C extension" or "without C extension".
[https://coverage.readthedocs.io/en/latest/install.html]

Testing sets up a test_database and should not interact with the project's
actual database.

1. To run tests with coverage (using Python-Coverage package):

$ coverage erase
$ coverage run manage.py test

2. To access the coverage data, you can either type:

$ coverage report 

to see the coverage report generated on-screen in the terminal, or 

$ coverage html

to generate a folder called htmlcov in the base directory. If you
open htmlcov/index.html, you'll see an easy to parse, color-coded 
version of the report with pretty tables.

Note that files with 100 percent coverage will not show up 
in the report. 