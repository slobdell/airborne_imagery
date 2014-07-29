from django.conf.urls import patterns, url

from .basic_navigation.views import home
from .basic_navigation.views import two_columns
from .basic_navigation.views import about
from .basic_navigation.views import calendar_month_year
from .basic_navigation.views import contact
from .basic_navigation.views import event
from .basic_navigation.views import events
from .basic_navigation.views import picture
from .basic_navigation.views import invoice
from .basic_navigation.views import privacy
from .basic_navigation.views import registration
from .basic_navigation.views import portfolio

urlpatterns = patterns('',
    url(r'^$', home, name='home'),
    url(r'^two_columns/$', two_columns),
    url(r'^about/$', about),
    url(r'^calendar/(?P<month>\d+)/(?P<year>\d+)/$', calendar_month_year),
    url(r'^contact/$', contact),
    url(r'^events/$', events),
    url(r'^event/(?P<event_id>\d+)/$', event, name='event'),
    url(r'^picture/(?P<picture_id>\d+)/$', picture, name='picture'),
    url(r'^invoice/$', invoice),
    url(r'^portfolio/$', portfolio),
    url(r'^privacy/$', privacy),
    url(r'^registration/$', registration),
)
