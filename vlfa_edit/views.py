from vlfa_base.models import Category, Thread, Post
from vlfa_base.utils import get_user_private_level

from django import forms
from django.views.generic.base import RedirectView
from django.views.generic.edit import UpdateView
from django.db import transaction
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect, get_object_or_404


class CreateTopicForm(forms.ModelForm):
    class Meta:
        model = Thread
        fields = ( 'title', )

class CreatePostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ( 'text_source', )


class CreateTopic(RedirectView):
    template_name = 'vlfa/create_topic.html'
    
    def get_redirect_url(self):
        return reverse('view-topic', kwargs={
                    'category_name': self.category.name,
                    'topic_id': self.thread.id})

    def get(self, request, *args, **kwargs):
        topic_form = CreateTopicForm()
        post_form = CreatePostForm()
        return render(request, self.template_name,
                     { 'topic_form': topic_form, 'post_form': post_form })
    
    def post(self, request, *args, **kwargs):
        topic_form = CreateTopicForm(request.POST)
        post_form = CreatePostForm(request.POST)
        
        if topic_form.is_valid() and post_form.is_valid():
            with transaction.commit_on_success():
                self.thread = topic_form.save(commit=False)
                self.thread.category = self.category
                self.thread.save()
                p = post_form.save(commit=False)
                p.thread = self.thread
                p.author = request.user
                p.save()
            return redirect(self.get_redirect_url())
        return render(request, self.template_name, 
                    { 'topic_form': topic_form, 'post_form': post_form })


    def dispatch(self, request, *args, **kwargs):
        category_name = self.kwargs.get('category_name', '')
        self.category = get_object_or_404(Category.on_site, name=category_name)
        if self.category.private_level > get_user_private_level(request.user):
            raise Http404
        return super(CreateTopic, self).dispatch(request, *args, **kwargs)
        


class CreatePost(RedirectView):
    template_name = 'vlfa/create_post.html'
    
    def get_redirect_url(self):
        return reverse('view-topic', kwargs={
                                     'category_name': self.category.name,
                                     'topic_id': self.thread.id})

    def get(self, request, *args, **kwargs):
        post_form = CreatePostForm()
        return render(request, self.template_name, { 'form': post_form }
    
    def post(self, request, *args, **kwargs):
        post_form = CreatePostForm(request.POST)
        if post_form.is_valid():
            p = post_form.save(commit=False)
            p.thread = self.thread
            p.author = request.user
            p.save()
            return redirect(self.get_redirect_url())
        return render(request, self.template_name, { 'form': post_form })

    def get_context_data(self, **kwargs):
        context = super(CreatePost, self).get_context_data(**kwargs)
        context['topic'] = self.thread
        return context
    
    def dispatch(self, request, *args, **kwargs):
        thread_id = kwargs.get('thread_id', 0)
        level = get_user_private_level(request.user)
        qs = Thread.on_site.filter(category__private_level__lte=level,
                                   is_closed=False)
        self.thread = get_object_or_404(qs, pk=thread_id)
        self.category = self.thread.category
        return super(CreatePost, self).dispatch(request, *args, **kwargs)


class EditPost(UpdateView):
    template_name = 'vlfa/edit_post.html'
    form_class = CreatePostForm()    

    def get_queryset(self):
        user = self.request.user
        level = get_user_private_level(self.request.user)
        return Post.active.filter(author=user)

    def get_context_data(self, **kwargs): 
        context = super(EditPost, self).get_context_data(**kwargs)
        context['topic'] = self.thread
        return context

 
        
