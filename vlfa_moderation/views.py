from vlfa_moderation.models import ModeratorProfile
from vlfa_base.models import Category, Thread, Post
from vlfa_base.views.categories import BrowseCategory, ViewTopic, ViewPost

from django.shortcuts import get_object_or_404, redirect
from django.http import Http404, HttpResponse

                  
class ModerateCategory(BrowseCategory):
    '''Render topic list on certain page but you can use extended post data'''
    template_name = 'vlfa/moderate_category.html'    
    template_move_topics = 'vlfa/move_topics.html'
    template_object_name = 'thread'

    def dispatch(self, request, category_name, *args, **kwargs):
        '''Check whether current user has rights for the moderating this category'''
        self.profile = get_object_or_404(ModeratorProfile.objects, user=request.user)
        category = get_object_or_404(Category.on_site, name=category_name)
        if category not in self.profile.categories:
            return HttpResponse(status=403)
        return super(ModerateCategory, self).dispatch(request, category_name, *args,
                                                      **kwargs)

    def post(self, request, category_name, page=None, *args, **kwargs):
        topic_ids = request.POST.getlist('topic_id')        
        if 'close_topics' in request.POST:
            Thread.on_site.filter(category__name=category_name,
                                  id__in=topic_ids).update(is_closed=True)
            return redirect('moderate-category', kwargs={'category_name': category_name,
                                                         'page': page })
        elif 'open_topics' in request.POST:
            Thread.on_site.filter(category__name=category_name,
                                  id__in=topic_ids).update(is_closed=False)
            return redirect('moderate-category', kwargs={'category_name': category_name,
                                                         'page': page})                
        elif 'delete_topics' in request.POST:
            Thread.on_site.filter(category__name=category_name,
                                  id__in=topic_ids).delete()
            return redirect('moderate-category', kwargs={'category_name': category_name,
                                                         'page': page})
        elif 'move_topics' in request.POST:
            return render(request, self.template_move_topics,
                    kwargs={ 'targets': Category.objects.exclude(name=category_name),
                             'topic_ids': topic_ids })

        return HttpResponse(status=400)
                             
    
class ModerateTopic(ViewTopic):
    template_name = 'vlfa/moderate_topic.html'
    template_object_name = 'post'

    def dispatch(self, request, category_name, topic_id, *args, **kwargs):
        self.profile = get_object_or_404(ModeratorProfile.objects, 
                                         user=request.user)
        category = get_object_or_404(Category.on_site, name=category_name)
        if category not in self.profile.categories:
            return HttpResponse(status=403)
        return super(ModerateCategory, self).dispatch(
                                request, category_name, topic_id,
                                *args, **kwargs)

    def post(self, request, category_name, topic_id, page=None, *args, **kwargs):
        post_ids = request.POST.getlist('post_id')
        if 'delete_posts' in request.POST:
            Post.on_site.filter(thread__category=category_name,
                                thread__pk=topic_id,
                                pk__in=post_ids).delete()
            return redirect('moderate-thread',
                             kwargs={ 'category_name': category_name,
                                      'topic_id': topic_id,
                                      'page': page})
        elif 'open_topic' in request.POST:
            thread = get_object_or_404(Thread.on_site,
                                       category__name=category_name,
                                       pk=topic_id)
            thread.is_closed = False
            thread.save()
        elif 'close_topic' in request.POST:
            thread = get_object_or_404(Thread.on_site,
                                       category__name=category_name,
                                       pk=topic_id)
            thread.is_closed = True
            thread.save()
        
        return HttpResponse(status=400)                
                                        

                                     
        
    
    
