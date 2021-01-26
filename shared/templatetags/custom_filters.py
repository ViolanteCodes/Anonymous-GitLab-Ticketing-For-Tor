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
def pretty_datetime(iso_string):
    """Takes an ISO 8601 Date-Time string and returns it in a pretty date format."""
    try:
        pretty_datetime = ''
        year = f"{iso_string[0]}{iso_string[1]}{iso_string[2]}{iso_string[3]}"
        month_digits = f"{iso_string[5]}{iso_string[6]}"
        if month_digits == '01':
            month = 'January'
        elif month_digits =='02':
            month = 'February'
        elif month_digits =='03':
            month = 'March'
        elif month_digits =='04':
            month = 'April'
        elif month_digits =='05':
            month = 'May'
        elif month_digits =='06':
            month = 'June'
        elif month_digits =='07':
            month = 'July'
        elif month_digits =='08':
            month = 'August'
        elif month_digits =='09':
            month = 'September'
        elif month_digits =='10':
            month = 'October'
        elif month_digits =='11':
            month = 'November'
        elif month_digits =='12':
            month = 'December'
        else:
            month = 'undefined'
        day = f"{iso_string[8]}{iso_string[9]}"
        time = f"{iso_string[11]}{iso_string[12]}{iso_string[13]}{iso_string[14]}{iso_string[15]}"
        pretty_datetime = f"{day} {month}, {year} - {time} UTC"
        return pretty_datetime
    except:
        pass
