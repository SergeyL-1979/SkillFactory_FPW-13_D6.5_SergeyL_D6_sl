from django.urls import path
from .views import *  # импортируем наше представление

urlpatterns = [
    path('', NewsList.as_view()),
    path('<int:pk>', NewsDetailView.as_view(), name='news_detail'),
    path('search/', NewsSearchView.as_view(), name='search'),
    path('add/', NewsCreateView.as_view(), name='news_create'),
    path('<int:pk>/edit/', NewsUpdateView.as_view(), name='news_update'),
    path('<int:pk>/delete/', NewsDeleteView.as_view(), name='news_delete'),

    path('category/<int:pk>', NewsCategoryListView.as_view(), name='category'),
    path('category/<int:pk>/subscribe/', Subscriber.as_view(), name='subscribe'),
]
