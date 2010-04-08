from django.conf import settings

class SiteErrorRouter(object):
	def db_for_read(self, model,  **hints):
		if model._meta.app_label == "django_site_errors":
			return getattr(settings,"SITE_ERROR_DBNAME","siteerrors")
		return None

	def db_for_write(self, model, **hints):
		if model._meta.app_label == "django_site_errors":
			return getattr(settings,"SITE_ERROR_DBNAME","siteerrors")
		return None
	
	def allow_syncdb(self, db, model):
		if db == getattr(settings,"SITE_ERROR_DBNAME","siteerrors"):
			return model._meta.app_label == "django_site_errors"

		elif model._meta.app_label == "django_site_errors":
			return False

		return None

	def allow_relation(self, obj1, obj2, **hints):
		if obj1._meta.app_label == 'django_site_errors' or obj2._meta.app_label == 'django_site_errors':
			return True
		return None
