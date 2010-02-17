from django.contrib import admin
from django.db import connection
from django.contrib.sites.models import Site

from coms.utils.site_errors import models as smodels

def resolve(modeladmin,request,queryset):
	"""
	BEGINHACK
	
	The below is in place to dump the error subscriptions from all sites into coms_orlando's
	db before sending out notifications. In the future, when multi-db support is out, we can
	trash this ugly nonsense in favor of simply having the subscription table in a central
	database for all projects from the get-go.

	For now, this is the answer. Before launching normal notifications, dump em all from the
	other databases into coms_orlando, and restrict this function to coms_orlando.
	"""

	current_site = Site.objects.get_current()
	if not current_site.domain == "orlando.comsnetwork.com":
		request.user.message_set.create(message="This function may only be executed at Orlando's COMS")
		return

	sql = "INSERT INTO coms_orlando.site_errors_siteerror (url, date_added, resolved, querystring, notification_done) SELECT url, date_added, resolved, querystring, notification_done FROM COMSDB.site_errors_siteerror WHERE url NOT IN (SELECT url FROM coms_orlando.site_errors_siteerror WHERE resolved = 0);INSERT INTO coms_orlando.site_errors_sitesubscriber (email) SELECT email FROM COMSDB.site_errors_sitesubscriber WHERE email NOT IN (SELECT email from coms_orlando.site_errors_sitesubscriber);INSERT INTO coms_orlando.site_errors_siteerror_email_subscribers (siteerror_id, sitesubscriber_id) SELECT T1.id, T2.id FROM coms_orlando.site_errors_siteerror T1 INNER JOIN COMSDB.site_errors_siteerror Z1 ON T1.url = Z1.url INNER JOIN COMSDB.site_errors_siteerror_email_subscribers Z2 ON Z1.id = Z2.siteerror_id INNER JOIN COMSDB.site_errors_sitesubscriber Z3 ON Z2.sitesubscriber_id = Z3.id INNER JOIN coms_orlando.site_errors_sitesubscriber T2 ON Z3.email = T2.email WHERE Z1.resolved = 0;TRUNCATE TABLE COMSDB.site_errors_siteerror;TRUNCATE TABLE COMSDB.site_errors_siteerror_email_subscribers;TRUNCATE TABLE COMSDB.site_errors_sitesubscriber;"

	slave_dbs = ['coms_demo','coms_volusia','coms_tally','coms_sarasota','facil_ftmyers','facil_careshare','facil_nfl','facil_nefl','facil_keys']

	cursor = connection.cursor()
	for db in slave_dbs:
		cursor.execute(sql.replace("COMSDB",db))
		
	cursor.close()

	"""
	ENDHACK
	"""
	for i in queryset:
		i.notify_and_resolve()

resolve.short_description = "Notify subscribers and resolve problem"

class SiteErrorAdmin(admin.ModelAdmin):
	list_display = ('url','resolved')
	actions = [resolve]
	list_filter = ('resolved',)

admin.site.register(smodels.SiteError,SiteErrorAdmin)
admin.site.register(smodels.SiteSubscriber)
