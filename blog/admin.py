from django.contrib import admin
from django.db.models import Count, Avg
from .models import BlogPost, Comment, PostLike, CommentLike, PostRating

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'get_comment_count', 'get_like_count', 'get_avg_rating')
    search_fields = ('title', 'content', 'author__username')
    list_filter = ('created_at', 'author')

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            _comment_count=Count('comments', distinct=True),
            _like_count=Count('likes', distinct=True),
            _avg_rating=Avg('ratings__rating')
        )

    def get_comment_count(self, obj):
        return obj._comment_count
    get_comment_count.short_description = 'Comments'

    def get_like_count(self, obj):
        return obj._like_count
    get_like_count.short_description = 'Likes'

    def get_avg_rating(self, obj):
        return f"{obj._avg_rating:.1f} ★" if obj._avg_rating else "No ratings"
    get_avg_rating.short_description = 'Avg Rating'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'parent', 'created_at')
    search_fields = ('content', 'author__username')

admin.site.register(PostLike)
admin.site.register(CommentLike)
admin.site.register(PostRating)
