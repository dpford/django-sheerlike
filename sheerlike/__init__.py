from __future__ import absolute_import  # Python 2 only

from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.urlresolvers import reverse
from django.conf import settings

from jinja2 import Environment

from unipath import Path

from .query import QueryFinder, more_like_this, get_document
from .filters import selected_filters_for_field, is_filter_selected
from .templates import date_formatter

PERMALINK_REGISTRY = {}


def register_permalink(sheer_type, url_pattern_name):
    PERMALINK_REGISTRY[sheer_type] = url_pattern_name


def url_for(app, filename):
    if app == 'static':
        return staticfiles_storage.url(filename)
    else:
        raise ValueError("url_for doesn't know about %s" % app)


def date_filter(value, format="%Y-%m-%d"):
    return date_formatter(value, format)


def is_active_nav(request, url):
    return request.path == url


def format_phone(num):
    assert len(num) == 10
    return '({}) {}-{}'.format(num[:3], num[3:6], num[6:])


def environment(**options):
    queryfinder = QueryFinder()

    searchpath = []
    staticdirs = []

    sites = settings.SHEER_SITES
    for site in sites:
        site_path = Path(site)
        searchpath.append(site_path)
        searchpath.append(site_path.child('_includes'))
        searchpath.append(site_path.child('_layouts'))
        staticdirs.append(site_path.child('static'))

    options['loader'].searchpath += searchpath
    settings.STATICFILES_DIRS = staticdirs

    env = Environment(**options)
    env.globals.update({
        'static': staticfiles_storage.url,
        'url_for': url_for,
        'url': reverse,
        'queries': queryfinder,
        'more_like_this': more_like_this,
        'get_document': get_document,
        'selected_filters_for_field': selected_filters_for_field,
        'is_filter_selected': is_filter_selected,
        'is_active_nav': is_active_nav,
    })
    env.filters.update({
        'date': date_filter,
        'format_phone': format_phone
    })
    return env
