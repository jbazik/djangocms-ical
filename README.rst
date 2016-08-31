====================================
iCalendar Feed Plugin for Django-CMS
====================================

Display events from an iCalendar feed (an ics file retrieved via http).

Features
--------

* Per-plugin template setting allows for varying views.

* Per-plugin setting controls number of events shown.

Requirements
------------

Requires:

* Django 1.7+

* Django-CMS 3.0+

Installation and Configuration
------------------------------
1. Install djangocms_ical

::

    pip install djangocms_ical

2. Add djangocms_ical to your INSTALLED_APPS

::

    INSTALLED_APPS = (
        ...,
        djangocms_ical,
        ...,
    )

3. Create djangocms_ical's database tables

::

    python manage.py migrate djangocms_ical

Settings
--------

DJANGOCMS_ICAL_TEMPLATES
  If DJANGOCMS_ICAL_TEMPLATES is defined, djangocms-ical offers authors an
  optional choice of a custom template.  The default template is
  ``djangocms_ical/ical.html``  Example::

    DJANGOCMS_ICAL_TEMPLATES = (
        ('brief.html', _('Brief')),
        ('expanded.html', _('Expanded')),
    )

DJANGOCMS_ICAL_EVENT_COUNT
  Default number of events to show.

DJANGOCMS_ICAL_CACHE_TIMEOUT
  Default time in seconds for plugins to cache the contents of a feed.
  If set to zero, feed content is not cached unless a timeout is set in
  each plugin.  The default is 0.

DJANGOCMS_ICAL_FEED_TIMEOUT
  Timeout, in seconds, for server requests for an iCalendar feed.  The
  default is 60.  Zero (0) means no timout, so don't do that.
