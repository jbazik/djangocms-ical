import sys
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
                cache.set(instance.url, feed, instance.cache_time)
            except (URLError, HTTPError, ValueError):
                feed = []
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
        n = 0
        for comp in cal.walk():
            if comp.name == 'VEVENT':
                events.append({k.lower(): comp.decoded(k) for k in comp.keys()})
        events.sort(key=lambda e: e['dtstart'])

        if instance.offset == 'NONE':
            return events[:instance.count]
        else:
            use_tz = getattr(settings, 'USE_TZ', False)
            now = timezone.now()
            if timezone.is_aware(events[0]['dtstart']) != use_tz:
                default_tz = timezone.get_default_timezone()
                if use_tz:
                    now = timezone.make_naive(now, default_tz)
                else:
                    now = timezone.make_aware(now, default_tz)
            if instance.offset == 'TODAY':
                # backup to midnight
                now.replace(hour=0, minute=0, second=0, microsecond=0)
            # find the next event
            for n in range(len(events)):
                if events[n]['dtstart'] >= now:
                    break
            if instance.offset == 'RECENT':
                return events[n-instance.count:n]
            elif instance.offset == 'ABOUT':
                return events[n-instance.count/2:n+instance.count/2]
            else:
                return events[n:n+instance.count]

plugin_pool.register_plugin(ICalPlugin)
