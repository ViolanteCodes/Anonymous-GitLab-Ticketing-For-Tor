# These next two lines are necessary for Django to recognize that 
# the following function calls are for custom filters.

from django import template
register = template.Library()

# Custom filters go here.
def pretty_date(string):
    """Takes an ISO 8601 Date-Time String and returns it in a pretty date."""
    try:
        pretty_date = ''
        year = f"{string[0]}{string[1]}{string[2]}{string[3]}"
        pretty_date = year
        return pretty_date
    except:
        pass

