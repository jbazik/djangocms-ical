from django.db import models
from django.conf import settings
from django.utils.translation import ugettext as _

from cms.models import CMSPlugin
from cms.utils.compat.dj import python_2_unicode_compatible

@python_2_unicode_compatible
class ICalModel(CMSPlugin):
    OFFSET = (
        ('NONE', _("All Events")),
        ('RECENT', _("Recent Events")),
        ('ABOUT', _("Recent and Upcoming Events")),
        ('TODAY', _("Today's and Upcoming Events")),
        ('NOW', _("Upcoming Events")),
    )
    TEMPLATES = [(value, label) for value, label in
                         getattr(settings, 'DJANGOCMS_ICAL_TEMPLATES', ())]
    offset = models.CharField(max_length=8, default='TODAY', choices=OFFSET)
    count = models.IntegerField(
                    default=getattr(settings, 'DJANGOCMS_ICAL_EVENT_COUNT', 5))
    url = models.URLField(max_length=512)
    cache_time = models.IntegerField(verbose_name=_("Cache time in seconds"),
                     default=getattr(settings, 'DJANGOCMS_ICAL_CACHE_TIME', 0))
    template = models.CharField(max_length=100, blank=True, default='',
                                                            choices=TEMPLATES)

    def __str__(self):
        return self.url
