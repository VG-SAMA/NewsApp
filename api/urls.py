from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('articles/', views.ArticleListAPIView.as_view(), name='api-articles'),
    path(
        'my-subscriptions/',
        views.MySubscriptionListAPIVIew.as_view(),
        name='api/my-subscriptions',
    ),
]
