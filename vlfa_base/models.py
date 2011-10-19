################################################################
## Part of Django-VLFA
## H3n0xek (c) 2011
## Code License: New BSD
################################################################

from django.db import models
from django.utils.translation import ugettext_lazy as _
from vlfa_base.managers import *
from datetime import datetime
from django.conf import settings as project_settings
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.urlresolvers import reverse


class Category(models.Model):
    name = models.CharField(max_length=30,
		help_text=_('This name will be as part of URL'),
		verbose_name=_('Category Name')
    )
    display_name = models.CharField(max_length=255,
                help_text=_('This name will be shown to forum users'),
		verbose_name=_('Display name')
    )
    pos = models.IntegerField(null=True, blank=True,
 		help_text=_('Position of category. Lower values will be shown earlier on the forum page'),
		verbose_name=_('Position')
    )
    private_level = models.IntegerField(null=True, blank=True,
		verbose_name=_('Private level'))
    site = models.ForeignKey(Site, default=project_settings.SITE_ID)

    objects = models.Manager()
    on_site = CategorySiteManager()

    def __unicode__(self):
        return u'%s' % self.display_name

    def get_absolute_url(self):
        return reverse('browse-category', kwargs={'category_name': self.name})

    def get_top_post(self):
        try:
            return Post.objects.filter(thread__category__id=self.pk).order_by('-pub_date')[0] # TODO: test   
        except IndexError:
            return []
	
    class Meta:        
        ordering = [ 'pos' ]
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')

        
class Thread(models.Model):
    category = models.ForeignKey(Category)	
    title = models.CharField(max_length=255,
		verbose_name=_('Topic title')
    )
	
    is_closed = models.BooleanField(default=False)	
    site = models.ForeignKey(Site, editable=False, default=project_settings.SITE_ID)
	
    objects = models.Manager()
    on_site = ThreadSiteManager()
    pub_date = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u'%s' % self.title	

    def get_absolute_url(self):
        return reverse('view-topic', kwargs={
            'category_name': self.category.name,
            'topic_id': self.pk})

    class Meta:        
        verbose_name = _('Thread')
        verbose_name_plural = _('Threads')
        ordering = [ '-pub_date' ]
	
    def get_topicstarter(self):
        return self.post_set.all()[0].author
	
    def get_last_post(self):
        return self.post_set.all()[self.post_set.count() -1]

        
class Post(models.Model):
    thread = models.ForeignKey(Thread)
    text_source = models.TextField()
    text = models.TextField()
    is_deleted = models.BooleanField(default=False)    
    pub_date = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    last_editor = models.ForeignKey(User, null=True, blank=True,
        related_name='+')
    author = models.ForeignKey(User, 
        related_name='+')
	
    objects = models.Manager()
    active = ActivePostsManager()
    deleted = DeletedPostsManager()

    def is_modified(self):
        return self.pub_date != self.last_modified
    
    def get_absolute_url(self):
        return reverse('view-topic', kwargs={
            'category_name': self.thread.category.name,
            'topic_id': self.thread.pk})

    def __unicode__(self):
        return u'%s: %s' % (self.author, self.thread)
	
    class Meta:        
        ordering = [ 'pub_date' ]
        verbose_name = _('Post')
        verbose_name_plural = _('Posts')


import markdown
@receiver(pre_save, sender=Post)
def compile_post_markdown(sender, instance, using, **kwargs):    
    instance.text = markdown.markdown(instance.text_source)
