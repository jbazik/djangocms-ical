import sys, datetime
try:
    from urllib.request import urlopen, Request
    from urllib.error import URLError, HTTPError
except ImportError:
    from urllib2 import urlopen, Request, URLError, HTTPError

from icalendar import Calendar

from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
from django.utils.translation import ugettext as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from djangocms_ical.models import ICalModel

use_tz = getattr(settings, 'USE_TZ', False)
default_tz = timezone.get_default_timezone()


class ICalPlugin(CMSPluginBase):
    model = ICalModel
    module = _("ICal")
    name = _("ICal Plugin")
    timeout = getattr(settings, 'DJANGOCMS_ICAL_FEED_TIMEOUT', 60)

    def get_render_template(self, context, instance, placeholder):
        if instance.template:
            return instance.template
        else:
            return "djangocms_ical/ical.html"

    def render(self, context, instance, placeholder):
        feed = cache.get(instance.url)
        if not feed:
            try:
                ics = self._get_ics(instance)
                feed = self._parse_ics(ics, instance)
                if not use_tz:
                    self._fix_timezone(feed)
                cache.set(instance.url, feed, instance.cache_time)
            except (URLError, HTTPError, ValueError):
                feed = []
        if use_tz:
            self._fix_timezone(feed)
        context.update({'instance': instance, 'feed': feed})
        return context

    def _get_ics(self, instance):
        try:
            resp = urlopen(instance.url, timeout=self.timeout)
        except URLError as e:
            sys.stderr.write(u"ERROR: %s [%s]" % (e.reason, instance.url))
            raise
        except HTTPError as e:
            reason = getattr(e, 'reason', e.read())
            sys.stderr.write(u"ERROR: %d %s [%s]" % (e.code, reason,
                                                     instance.url))
            raise
        return resp.read()

    def _parse_ics(self, ics, instance):
        try:
            cal = Calendar.from_ical(ics)
        except ValueError as e:
            sys.stderr.write(u"ERROR: invalid ics content [%s]" % instance.url)
            raise
        events = []
        for comp in cal.walk():
            if comp.name == 'VEVENT':
                event = {k.lower(): comp.decoded(k) for k in comp.keys()}
                #
                # use timezone aware datetimes for sorting
                #
                if isinstance(event['dtstart'], datetime.datetime):
                    event['_time'] = event['dtstart']
                elif isinstance(event['dtstart'], datetime.date):
                    event['_time'] = datetime.datetime.combine(event['dtstart'],
                                                       datetime.time.min)
                if timezone.is_naive(event['_time']):
                    event['_time'] = timezone.make_aware(event['_time'],
                                                         default_tz)
                events.append(event)
        if not events:
            return []

        events.sort(key=lambda e: e['_time'])

        if instance.offset == 'NONE':
            return events[:instance.count]
        else:
            now = timezone.make_aware(timezone.now())
            if instance.offset == 'TODAY':
                # backup to midnight
                now.replace(hour=0, minute=0, second=0, microsecond=0)
            # find the next event
            for n in range(len(events)):
                if events[n]['_time'] >= now:
                    break
            if instance.offset == 'RECENT':
                left = n - instance.count if n > instance.count else 0
                return events[n-instance.count:n]
            elif instance.offset == 'ABOUT':
                halfcnt = int(instance.count / 2)
                left = n - halfcnt if n > halfcnt else 0
                return events[left:n+halfcnt]
            else:
                return events[n:n+instance.count]

    def _fix_timezone(self, feed):
        tz = timezone.get_current_timezone() if use_tz else default_tz
        for event in feed:
            for attr in 'dtstart', 'dtend':
                if attr in event and hasattr(event[attr], 'tzinfo'):
                    if event[attr].tzinfo is None:
                        event[attr].replace(tzinfo=default_tz)
                    if event[attr].tzinfo != tz:
                        event[attr] = event[attr].astimezone(tz)

plugin_pool.register_plugin(ICalPlugin)
