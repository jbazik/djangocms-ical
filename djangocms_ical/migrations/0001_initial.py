# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0013_urlconfrevision'),
    ]

    operations = [
        migrations.CreateModel(
            name='ICalModel',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
                ('offset', models.CharField(default=b'TODAY', max_length=8, choices=[(b'NONE', 'All Events'), (b'RECENT', 'Recent Events'), (b'ABOUT', 'Recent and Upcoming Events'), (b'TODAY', "Today's and Upcoming Events"), (b'NOW', 'Upcoming Events')])),
                ('count', models.IntegerField(default=5)),
                ('url', models.URLField(max_length=512)),
                ('cache_time', models.IntegerField(default=0, verbose_name='Cache time in seconds')),
                ('template', models.CharField(default=b'', max_length=100, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
    ]
