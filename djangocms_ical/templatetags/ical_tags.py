from datetime import datetime

from django import template

register = template.Library()


@register.simple_tag
def event_time_long(event):
    start = event['dtstart']
    if 'dtend' in event:
        end = event['dtend']
    elif 'duration' in event:
        end = start + event['duration']
    else:
        return start.strftime("%A, %B %-d %-I:%M%p")

    if start.date() == end.date():
        return(start.strftime("%A, %B %-d %-I:%M%p - ") +
               end.strftime("%I:%M%p"))
    else:
        return(start.strftime("%A, %B %-d %-I:%M%p - ") +
               end.strftime("%A, %B %-d %-I:%M%p"))

@register.simple_tag
def event_time_short(event):
    start = event['dtstart']
    if 'dtend' in event:
        end = event['dtend']
    elif 'duration' in event:
        end = start + event['duration']
    else:
        return start.strftime("%a, %x %-I:%M%p", start)

    if start.date() == end.date():
        return(start.strftime("%a, %x %-I:%M%p - ") +
               end.strftime("%I:%M%p"))
    else:
        return(start.strftime("%a, %x %-I:%M%p - ") +
               end.strftime("%a, %x %-I:%M%p"))
