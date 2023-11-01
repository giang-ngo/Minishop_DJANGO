from django.urls import path
from .import views

urlpatterns = [
    path('', views.posts_list, name='posts_list'),
    path('tag/<slug:tag_slug>/', views.tagged, name='tag'),
    path('category/<slug:category_slug>/',
         views.posts_list, name='posts_by_category'),
    path('category/<slug:category_slug>/<slug:post_slug>/',
         views.post_detail, name='post_detail'),
         

]
