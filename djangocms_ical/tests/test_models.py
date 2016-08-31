from django.test import TestCase

from djangocms_ical import models

class ModelTests(TestCase):

    def test_plugin_object(self):
        plugin = models.ICalModel()
        self.assertTrue(plugin)
