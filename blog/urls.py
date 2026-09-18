from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('popular/', views.popular_posts, name='popular_posts'),
    path('search/', views.search_posts, name='search_posts'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/new/', views.create_post, name='create_post'),
    path('post/<int:pk>/edit/', views.edit_post, name='edit_post'),
    path('post/<int:pk>/delete/', views.delete_post, name='delete_post'),
    path('my-posts/', views.my_posts, name='my_posts'),
    
    # Module 10 routes
    path('post/<int:post_pk>/comment/', views.add_comment, name='add_comment'),
    path('comment/<int:pk>/edit/', views.edit_comment, name='edit_comment'),
    path('comment/<int:pk>/delete/', views.delete_comment, name='delete_comment'),
    path('post/<int:pk>/like/', views.toggle_post_like, name='toggle_post_like'),
    path('comment/<int:pk>/like/', views.toggle_comment_like, name='toggle_comment_like'),
    path('post/<int:pk>/rate/', views.rate_post, name='rate_post'),
    path('profile/<str:username>/', views.user_profile, name='user_profile'),
]
