import sys, re, datetime
import pytz
from io import StringIO
from mock import patch

try:
    from urllib.error import HTTPError
except ImportError:
    from urllib2 import HTTPError

from django.test import TestCase
from django.test.client import RequestFactory
from django.template import Context

from cms.api import add_plugin
from cms.models import Placeholder

from djangocms_ical.cms_plugins import ICalPlugin


class GetICS(object):
    #
    # file-like object to mock urlopen return value
    #
    def __init__(self, file, code=200):
        self.file = file
        self.code = code
        self.headers = {'content-type': 'text/calendar'}

    def geturl(self):
        return self.file

    def getcode(self):
        return self.code

    def read(self):
        #
        # The plugin references the current time, so the test data
        # is adjusted to the current time here.
        #
        dday = datetime.timedelta(days=1)
        now = datetime.datetime.now(pytz.utc)
        yesterday = (now - dday).strftime("%Y%m%d")
        tomorrow = (now + dday).strftime("%Y%m%d")
        plustwo = (now + dday * 2).strftime("%Y%m%d")
        ics = open(self.file, 'r').read()
        ics = re.sub(r'\$\(YESTERDAY\)', yesterday, ics)
        ics = re.sub(r'\$\(TOMORROW\)', tomorrow, ics)
        ics = re.sub(r'\$\(PLUSTWO\)', plustwo, ics)
        return ics

class PluginTests(TestCase):
    test_ics = 'djangocms_ical/tests/test.ics'

    def setUp(self):
        self.placeholder = Placeholder.objects.create(slot="test")
        self.patcher = patch('djangocms_ical.cms_plugins.urlopen')
        self.urlopen_mock = self.patcher.start()

    def create_plugin(self, file, code):
        self.urlopen_mock.return_value = GetICS(file, code)
        self.object = add_plugin(self.placeholder, ICalPlugin, 'en')
        self.object.offset = 'NONE'
        self.object.url = file
        self.object.save()

    def create_context(self):
        self.req =RequestFactory().get('/')
        self.req.current_page = None
        self.context = Context({'request': self.req,
                                'object': self.object,
                                'current_app': 'test_app'})

    def tearDown(self):
        self.patcher.stop()

    def test_html(self):
        self.create_plugin(self.test_ics, 200)
        self.create_context()
        html = self.object.render_plugin(self.context)
        self.assertIn('Event Number 1', html)
        self.assertIn('Event Number 2', html)
        self.assertIn('Event Number 3', html)

    def test_context(self):
        self.create_plugin(self.test_ics, 200)
        self.create_context()
        plugin = self.object.get_plugin_class_instance()
        context = plugin.render(self.context, self.object, self.placeholder)
        self.assertIn('instance', context)
        self.assertEqual(context['instance'].id, self.object.id)
        self.assertIn('feed', context)
        feed = context['feed']
        self.assertEqual(len(feed), 4)

        self.assertRaises(KeyError, lambda: feed[0]['duration'])
        self.assertEqual(feed[0]['summary'], b'Event Number 4 Summary')
        self.assertEqual(feed[0]['uid'], 'fakeuid@google.com')

        self.assertEqual(feed[1]['duration'], datetime.timedelta(hours=2))
        self.assertListEqual(feed[1]['categories'],
                             [b'Category 1', b'Category 2'])
        self.assertEqual(feed[1]['summary'], b'Event Number 1 Summary')
        self.assertEqual(feed[1]['location'], b'Location 1')
        self.assertEqual(feed[1]['url'], 'http://example.com/Event/1/')

        self.assertEqual(feed[2]['dtend'] - feed[2]['dtstart'],
                         datetime.timedelta(hours=1))
        self.assertEqual(feed[2]['categories'], b'Category 1')
        self.assertEqual(feed[2]['summary'], b'Event Number 2 Summary')
        self.assertEqual(feed[2]['location'], b'Location 2')
        self.assertEqual(feed[2]['url'], 'http://example.com/Event/2/')

        self.assertEqual(feed[3]['categories'], b'Category 2')
        self.assertEqual(feed[3]['dtend'] - feed[3]['dtstart'],
                         datetime.timedelta(days=1))
        self.assertEqual(feed[3]['summary'], b'Event Number 3 Summary')
        self.assertEqual(feed[3]['location'], b'Location 2')
        self.assertEqual(feed[3]['url'], 'http://example.com/Event/3/')

    def test_offset(self):
        self.create_plugin(self.test_ics, 200)
        self.create_context()
        plugin = self.object.get_plugin_class_instance()
        context = plugin.render(self.context, self.object, self.placeholder)
        self.assertEqual(len(context['feed']), 4)
        self.object.offset = 'RECENT'
        context = plugin.render(self.context, self.object, self.placeholder)
        self.assertEqual(len(context['feed']), 1)
        self.object.offset = 'ABOUT'
        context = plugin.render(self.context, self.object, self.placeholder)
        self.assertEqual(len(context['feed']), 4)
        self.object.offset = 'TODAY'
        context = plugin.render(self.context, self.object, self.placeholder)
        self.assertEqual(len(context['feed']), 2)
        self.object.offset = 'NOW'
        context = plugin.render(self.context, self.object, self.placeholder)
        self.assertEqual(len(context['feed']), 2)

    def test_not_found(self):
        self.create_plugin(self.test_ics, 404)
        self.create_context()
        self.urlopen_mock.side_effect = HTTPError(self.test_ics, 404,
                                                  "Not Found", None, None)
        with patch('sys.stderr', new=StringIO()) as stderr:
            html = self.object.render_plugin(self.context)
            stderr.seek(0)
            self.assertIn('ERROR: Not Found', stderr.read())
            stderr.seek(0)
            self.assertIn(self.test_ics, stderr.read())
        self.assertIn('No events', html)
