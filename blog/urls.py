from django.urls import path
from .import views

urlpatterns = [
    path('', views.posts_list, name='posts_list'),
    path('post_create/', views.post_create, name='post_create'),
    path('post_update/<slug:post_slug>/', views.post_update, name='post_update'),
    path('post_delete/<slug:post_slug>/', views.post_delete, name='post_delete'),


    path('tag/<slug:tag_slug>/', views.tagged, name='tag'),
    path('category/<slug:category_slug>/',
         views.posts_list, name='posts_by_category'),
    path('category/<slug:category_slug>/<slug:post_slug>/',
         views.post_detail, name='post_detail'),
    path('search/', views.search, name='search'),
    path('comment/<int:post_id>/', views.comment, name='comment'),



]
