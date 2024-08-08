from . import views
from rest_framework.routers import DefaultRouter
from django.urls import path

app_name = 'post'

router = DefaultRouter()
router.register('post', views.PostModelViewSet, basename='post')

urlpatterns = [
    path('vote/', views.VoteApiView.as_view(), name='vote'),
]
urlpatterns += router.urls