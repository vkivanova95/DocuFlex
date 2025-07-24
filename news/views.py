from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, UpdateView
from .models import NewsPost
from common.mixins import GroupRequiredMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from .forms import NewsPostForm
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from logs.mixins import LogActionMixin


class PublicHomepageView(ListView):
    model = NewsPost
    template_name = 'news/welcome.html'
    context_object_name = 'news_posts'

    def get_queryset(self):
        return NewsPost.objects.filter(is_active=True).order_by('-published_at')


class NewsPostCreateView(LoginRequiredMixin, GroupRequiredMixin, LogActionMixin, CreateView):
    model = NewsPost
    form_class = NewsPostForm
    template_name = 'news/add_news.html'
    success_url = reverse_lazy('news:news_list')
    success_message = "Новината беше успешно добавена."
    allowed_groups = ['ръководител']
    action_type = 'create'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, self.success_message)
        return response


class NewsPostListView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    model = NewsPost
    template_name = 'news/news_list.html'
    context_object_name = 'news_posts'
    paginate_by = 10
    allowed_groups = ['ръководител']

    def get_queryset(self):
        return NewsPost.objects.all().order_by('-published_at')


class NewsPostUpdateView(LoginRequiredMixin, GroupRequiredMixin, LogActionMixin, UpdateView):
    model = NewsPost
    form_class = NewsPostForm
    template_name = 'news/add_news.html'
    success_url = reverse_lazy('news:news_list')
    allowed_groups = ['ръководител']
    action_type = 'edit'


class NewsPostDeactivateView(LoginRequiredMixin, GroupRequiredMixin, SuccessMessageMixin, View):
    allowed_groups = ['ръководител']

    def post(self, request, pk):
        news_post = get_object_or_404(NewsPost, pk=pk)
        if news_post.is_active:
            news_post.is_active = False
            news_post.save()
            messages.success(request, "Новината беше деактивирана.")
        else:
            messages.warning(request, "Новината вече е деактивирана.")
        return redirect('news:news_list')
