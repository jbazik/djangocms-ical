from setuptools import find_packages, setup
from djangocms_ical import __version__

setup (
    name='djangocms-ical',
    version=__version__,
    packages=find_packages(),
    provides = ['djangocms_ical'],
    include_package_data = True,
    license = 'BSD',
    description='Display events from an iCalendar feed',
    author='John Bazik',
    author_email='jsb@cs.brown.edu',
    url='http://github.com/jbazik/djangocms-ical',
    install_requires = [
        'Django>=1.7',
        'django-cms>=3.0',
        'icalendar',
    ],
    test_suite = 'djangocms_ical.tests.test_models',
    tests_require = [
        'mock',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
        'License :: OSI Approved :: BSD License',
    ],
)
