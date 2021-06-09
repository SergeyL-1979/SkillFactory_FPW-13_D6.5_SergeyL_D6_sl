from django.urls import path
from .views import *  # импортируем наше представление

urlpatterns = [
    path('', NewsList.as_view()),
    path('<int:pk>', NewsDetailView.as_view(), name='news_detail'),
    path('search/', NewsSearchView.as_view(), name='search'),
    path('add/', NewsCreateView.as_view(), name='news_create'),
    path('<int:pk>/edit/', NewsUpdateView.as_view(), name='news_update'),
    path('<int:pk>/delete/', NewsDeleteView.as_view(), name='news_delete'),

    # path('subscribe/<int:pk>', subscribe_me),
    # path('unsubscribe/<int:pk>', unsubscribe_me),
    path('category/subscribe/<int:pk>', subscribe_me),
    path('category/unsubscribe/<int:pk>', unsubscribe_me),

    path('<int:pk>', CategorySubscribe.as_view(), name='subscribe'),

    # path('subscribe/<int:pk>', subscribe_view, name='subscribe_view'),
    # path('category/', NewsCategoryListView.as_view(), name='category'),
]
