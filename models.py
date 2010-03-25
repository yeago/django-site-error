import datetime
from sets import Set

from django.db import models
from django.conf import settings
from django.template.loader import get_template
from django.template import Context

from django.core.mail import send_mail

from django.contrib.sites.models import Site

class SiteError(models.Model):
	url = models.CharField(max_length=255)
	date_added = models.DateTimeField()
	resolved = models.BooleanField(default=False)
	querystring = models.TextField(null=True,blank=True)
	user_subscribers = models.ManyToManyField('auth.User',blank=True)
	email_subscribers = models.ManyToManyField('django_site_errors.SiteSubscriber',blank=True)
	notification_done = models.BooleanField(default=False,editable=False)
	def notify_and_resolve(self):
		site = Site.objects.get_current()

		email_context = {'site_url': site.domain, 'problem_url': self.url, 'problem_querystring': None}

		subject_template = get_template('django_site_errors/email_subject.txt')
		subject = subject_template.render(Context(email_context))
		subscribers = Set(self.user_subscribers.values_list('email',flat=True).distinct()).union(\
				Set(self.email_subscribers.values_list('email',flat=True).distinct()))

		body_template = get_template('django_site_errors/email_body.txt')
		body = body_template.render(Context(email_context))

		for i in subscribers:
			send_mail(subject.strip('\n'),body,settings.DEFAULT_FROM_EMAIL,[i])

		self.notification_done = True
		self.resolved = True
		self.save()

	def save(self,*args,**kwargs):
		if not self.date_added:
			self.date_added = datetime.datetime.now()

		super(SiteError,self).save(*args,**kwargs)

"""
This is handy not only for allowing unauth'd users to subscribe,
and also for allowing logged in users from many different projects
to subscribe to the same issue, in the event a project is running
serially for many databases.
"""

class SiteSubscriber(models.Model):
	email = models.EmailField()
	def __unicode__(self):
		return self.email
