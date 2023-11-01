from .models import PostingCategory


def post_category_links(request):
    post_categories = PostingCategory.objects.all()
    return dict(post_categories=post_categories)
