from django.conf import settings
from django.shortcuts import render_to_response,redirect
from django.http import Http404, HttpResponseServerError
from django.template.loader import get_template
from django.template import RequestContext

from django_site_errors import models as smodels

def subscribe_email(request):
	if not request.GET.get('email') and not request.user.is_authenticated():
		raise Http404

	error_path = request.GET.get('error_path',"/%s" % request.META['HTTP_REFERER'].split('/',3)[3])
	site_error = smodels.SiteError.objects.get_or_create(url=error_path)[0]
	subscriber = smodels.SiteSubscriber.objects.get_or_create(email=request.GET.get('email',request.user.email))[0]
	site_error.email_subscribers.add(subscriber)
	request.user.message_set.create(message="You will be notified when that problem is resolved")
	return redirect(request.GET.get('return_url','/'))


def handler500(request):
	template = get_template('500.html')
	return HttpResponseServerError(template.render(RequestContext(request,{'MEDIA_URL': settings.MEDIA_URL})))
