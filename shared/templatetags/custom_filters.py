# These next two lines are necessary for Django to recognize that 
# the following function calls are for custom filters.

from django import template
from django.template.defaultfilters import stringfilter
register = template.Library()

# Custom filters go here.

# Register filter with library and define it as a function that only 
# takes strings to avoid AttributeErrors

@register.filter(is_safe=True)
@stringfilter
def pretty_date(iso_string):
    """Takes an ISO 8601 Date-Time string and returns it in a pretty date format."""
    try:
        pretty_date = ''
        year = f"{iso_string[0]}{iso_string[1]}{iso_string[2]}{iso_string[3]}"
        month = f"{iso_string[5]}{iso_string[6]}"
        day = f"{iso_string[8]}{iso_string[9]}"
        time = f"{iso_string[11]}{iso_string[12]}{iso_string[13]}{iso_string[14]}{iso_string[15]}"
        pretty_date = f"{month}/{day}/{year} - {time} UTC"
        return pretty_date
    except:
        pass

