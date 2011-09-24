from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.http import Http404
from vlfa_base.models import Category, Thread, Post
from vlfa_base.settings import THREADS_PER_PAGE, POSTS_PER_PAGE
from vlfa_base.utils import get_user_private_level


class ListCategories(ListView):
    template_name = 'vlfa/list_categories.html'
    template_object_name = 'category'

    def get_queryset(self):
        u = self.request.user
        return Category.objects.filter(private_level__lte = \
                                      get_user_private_level(u))
    
class BrowseCategory(ListView):
    template_name = 'vlfa/browse_category.html'
    template_object_name = 'thread'

    def get_queryset(self):
        u = self.request.user
        name = self.kwargs.get('category_name', None)
        if not name:
            raise Http404
        try:
            self.category = Category.objects.filter(
                                private_level__lte = get_user_private_level(u),
                                name=name).get()
        except Category.DoesNotExist:
            raise Http404
        return self.category.thread_set.all()

    def get_context_data(self, **kwargs):
        context = super(BrowseCategory, self).get_context_data(**kwargs)
        context['category'] = self.category
        return context


class ViewTopic(ListView):
    template_name = 'vlfa/view_topic.html'
    template_object_name = 'post'
    paginate_by = POSTS_PER_PAGE

    def get_queryset(self):
        u = self.request.user
        category_name = self.kwargs.get('category_name', None)
        topic_id = int(self.kwargs.get('topic_id', None))
        if not category_name or not topic_id:
            raise Http404
        try:
            self.category = Category.on_site.filter(
                            private_level__lte = get_user_private_level(u),
                            name=category_name).get()
            self.topic = self.category.thread_set.get(pk=topic_id)
        except (Category.DoesNotExist, Topic.DoesNotExist):
            raise Http404

        return Post.active.filter(thread=self.topic)

    def get_context_data(self, **kwargs):
        context = super(ViewTopic, self).get_context_data(**kwargs)
        context['category'] = self.category
        context['topic'] = self.topic
        return context


class ViewPost(DetailView):
    template_name = 'vlfa/view_post.html'
    context_object_name = 'post'
    
    def get_queryset(self):
        u = self.request.user
        level = get_user_private_level(u)
        return Post.active.filter(thread__category__private_level__lte=level)

    def get_object(self, queryset=None):
        object = super(ViewPost, self).get_object(queryset)
        self.topic = object.thread
        self.category = object.thread.category
        return object    
                                
    def get_context_data(self, **kwargs):
        context = super(ViewPost, self).get_context_data(**kwargs)
        context['topic'] = self.topic
        context['category'] = self.category
        return context        
        
