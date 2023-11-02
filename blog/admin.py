from django.contrib import admin
from .models import Post, PostingCategory, Comment


class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'status', 'category', 'created_on')
    list_filter = ("status", )
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}


class PostingCategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name', 'slug',)
    prepopulated_fields = {'slug': ('category_name',)}


class CommentAdmin(admin.ModelAdmin):
    list_display = ['post', 'user', 'body']


admin.site.register(PostingCategory, PostingCategoryAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
