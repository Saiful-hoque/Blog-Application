from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.db.models import Count, Avg, Q
from django.contrib.auth.models import User
from .models import BlogPost, Comment, PostLike, CommentLike, PostRating
from .forms import BlogPostForm, CommentForm, RatingForm

def home(request):
    # Query Optimization: select_related for author (One-to-Many foreign key)
    # Aggregation & Annotation: Count likes, Count comments, Avg rating
    posts = BlogPost.objects.select_related('author').annotate(
        total_likes=Count('likes', distinct=True),
        total_comments=Count('comments', distinct=True),
        avg_rating=Avg('ratings__rating')
    ).order_by('-created_at')
    return render(request, 'blog/home.html', {'posts': posts})

def popular_posts(request):
    # Advanced ORM: Annotation + Ordering by engagement metrics
    posts = BlogPost.objects.select_related('author').annotate(
        total_likes=Count('likes', distinct=True),
        total_comments=Count('comments', distinct=True),
        avg_rating=Avg('ratings__rating')
    ).order_by('-total_likes', '-avg_rating', '-total_comments')[:10]
    return render(request, 'blog/popular_posts.html', {'posts': posts})

def search_posts(request):
    query = request.GET.get('q', '').strip()
    min_rating = request.GET.get('rating', '').strip()

    posts = BlogPost.objects.select_related('author').annotate(
        total_likes=Count('likes', distinct=True),
        total_comments=Count('comments', distinct=True),
        avg_rating=Avg('ratings__rating')
    )

    # Advanced Queries: title__icontains, content__icontains, author__username
    if query:
        posts = posts.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(author__username__icontains=query)
        )
    if min_rating:
        try:
            posts = posts.filter(avg_rating__gte=float(min_rating))
        except ValueError:
            pass

    return render(request, 'blog/search_results.html', {'posts': posts, 'query': query, 'min_rating': min_rating})

def post_detail(request, pk):
    # Query Optimization: select_related(author) and prefetch_related for nested replies & likes
    post = get_object_or_404(
        BlogPost.objects.select_related('author').annotate(
            total_likes=Count('likes', distinct=True),
            total_comments=Count('comments', distinct=True),
            avg_rating=Avg('ratings__rating'),
            total_ratings=Count('ratings', distinct=True)
        ),
        pk=pk
    )

    # Root comments with author, likes, and recursive replies
    comments = post.comments.filter(parent=None).select_related('author').prefetch_related(
        'likes',
        'replies__author',
        'replies__likes',
        'replies__replies__author',
        'replies__replies__likes'
    )

    user_liked = False
    user_rating = None
    if request.user.is_authenticated:
        user_liked = post.likes.filter(user=request.user).exists()
        rating_obj = post.ratings.filter(user=request.user).first()
        if rating_obj:
            user_rating = rating_obj.rating

    comment_form = CommentForm()
    rating_form = RatingForm(initial={'rating': user_rating} if user_rating else None)

    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'rating_form': rating_form,
        'user_liked': user_liked,
        'user_rating': user_rating,
    }
    return render(request, 'blog/post_detail.html', context)

@login_required
def add_comment(request, post_pk):
    post = get_object_or_404(BlogPost, pk=post_pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            parent_id = request.POST.get('parent_id')
            if parent_id:
                parent_comment = get_object_or_404(Comment, pk=parent_id)
                comment.parent = parent_comment
            comment.save()
            messages.success(request, 'Comment added successfully!')
    return redirect('post_detail', pk=post.pk)

@login_required
def edit_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if comment.author != request.user:
        raise PermissionDenied("You are not authorized to edit this comment.")
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Comment updated successfully!')
            return redirect('post_detail', pk=comment.post.pk)
    else:
        form = CommentForm(instance=comment)
    return render(request, 'blog/edit_comment.html', {'form': form, 'comment': comment})

@login_required
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    post_pk = comment.post.pk
    if comment.author != request.user:
        raise PermissionDenied("You are not authorized to delete this comment.")
    if request.method == 'POST':
        comment.delete()
        messages.success(request, 'Comment deleted successfully!')
        return redirect('post_detail', pk=post_pk)
    return render(request, 'blog/delete_comment.html', {'comment': comment})

@login_required
def toggle_post_like(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    like_obj = PostLike.objects.filter(post=post, user=request.user).first()
    if like_obj:
        like_obj.delete()
        messages.info(request, 'Post unliked.')
    else:
        PostLike.objects.create(post=post, user=request.user)
        messages.success(request, 'Post liked!')
    return redirect('post_detail', pk=post.pk)

@login_required
def toggle_comment_like(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    like_obj = CommentLike.objects.filter(comment=comment, user=request.user).first()
    if like_obj:
        like_obj.delete()
    else:
        CommentLike.objects.create(comment=comment, user=request.user)
    return redirect('post_detail', pk=comment.post.pk)

@login_required
def rate_post(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    if request.method == 'POST':
        rating_val = request.POST.get('rating')
        if rating_val and 1 <= int(rating_val) <= 5:
            PostRating.objects.update_or_create(
                post=post,
                user=request.user,
                defaults={'rating': int(rating_val)}
            )
            messages.success(request, f'You rated this post {rating_val}/5 stars!')
    return redirect('post_detail', pk=post.pk)

@login_required
def user_profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    # Aggregations for user profile statistics
    total_posts = profile_user.blog_posts.count()
    total_comments = profile_user.user_comments.count()
    likes_given = profile_user.post_likes.count() + profile_user.comment_likes.count()
    ratings_given = profile_user.post_ratings.count()

    user_posts = profile_user.blog_posts.annotate(
        total_likes=Count('likes', distinct=True),
        total_comments=Count('comments', distinct=True),
        avg_rating=Avg('ratings__rating')
    )

    context = {
        'profile_user': profile_user,
        'total_posts': total_posts,
        'total_comments': total_comments,
        'likes_given': likes_given,
        'ratings_given': ratings_given,
        'user_posts': user_posts
    }
    return render(request, 'users/profile.html', context)

@login_required
def create_post(request):
    if request.method == 'POST':
        form = BlogPostForm(request.POST)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.author = request.user
            blog.save()
            messages.success(request, 'Blog post created successfully!')
            return redirect('post_detail', pk=blog.pk)
    else:
        form = BlogPostForm()
    return render(request, 'blog/create_post.html', {'form': form})

@login_required
def edit_post(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    if post.author != request.user:
        raise PermissionDenied("You are not authorized to edit this post.")
    if request.method == 'POST':
        form = BlogPostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Blog post updated successfully!')
            return redirect('post_detail', pk=post.pk)
    else:
        form = BlogPostForm(instance=post)
    return render(request, 'blog/edit_post.html', {'form': form, 'post': post})

@login_required
def delete_post(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    if post.author != request.user:
        raise PermissionDenied("You are not authorized to delete this post.")
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Blog post deleted successfully!')
        return redirect('home')
    return render(request, 'blog/delete_post.html', {'post': post})

@login_required
def my_posts(request):
    posts = BlogPost.objects.filter(author=request.user).annotate(
        total_likes=Count('likes', distinct=True),
        total_comments=Count('comments', distinct=True),
        avg_rating=Avg('ratings__rating')
    )
    return render(request, 'blog/my_posts.html', {'posts': posts})
