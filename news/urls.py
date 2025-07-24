from django.urls import path
from .views import PublicHomepageView, NewsPostCreateView, NewsPostListView, NewsPostUpdateView, NewsPostDeactivateView

app_name = 'news'

urlpatterns = [
    path('', PublicHomepageView.as_view(), name='welcome'),
    path('add/', NewsPostCreateView.as_view(), name='add_news'),
    path('all/', NewsPostListView.as_view(), name='news_list'),
    path('edit/<int:pk>/', NewsPostUpdateView.as_view(), name='edit_news'),
    path('deactivate/<int:pk>/', NewsPostDeactivateView.as_view(), name='deactivate_news'),
]