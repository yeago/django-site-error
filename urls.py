from django.conf.urls.defaults import *

urlpatterns = patterns('coms.utils.site_errors.views',
	url('^site-errors/subscribe/$', 'subscribe_email', name="siteerror_subscribe_email"),
)
