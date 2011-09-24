from django.db import models
from django.conf import settings


class CategorySiteManager(models.Manager):
    def get_query_set(self):
        return super(CategorySiteManager, self).get_query_set().filter(
            site__pk=settings.SITE_ID)


class ThreadSiteManager(models.Manager):
    def get_query_set(self):
        return super(ThreadSiteManager, self).get_query_set().filter(
            site__pk=settings.SITE_ID)


class ActivePostsManager(models.Manager):
    def get_query_set(self):
        return super(ActivePostsManager, self).get_query_set().filter(
            is_deleted=False)


class DeletedPostsManager(models.Manager):
    def get_query_set(self):
        return super(DeletedPostsManager, self).get_query_set().filter(
            is_deleted=True)
