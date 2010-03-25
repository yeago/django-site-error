from django.contrib import admin
from django.db import connection
from django.contrib.sites.models import Site

from django_site_errors import models as smodels

def resolve(modeladmin,request,queryset):
	for i in queryset:
		i.notify_and_resolve()

resolve.short_description = "Notify subscribers and resolve problem"

class SiteErrorAdmin(admin.ModelAdmin):
	list_display = ('url','resolved')
	actions = [resolve]
	list_filter = ('resolved',)

admin.site.register(smodels.SiteError,SiteErrorAdmin)
admin.site.register(smodels.SiteSubscriber)
