from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from .models import Post
from .forms import CommentForm
from django.core.paginator import Paginator
from backoffice.models import Ad

def post_list(request):
    last_post_news = Post.objects.filter(type='news', status='published').order_by('-created_at')[:6]
       # Requêtes
    _last_post_contrib = Post.objects.filter(type='contribution', status='published').order_by('-created_at')
    _old_post_news = Post.objects.filter(type='news', status='published').order_by('created_at')

    # Pagination contributions (6 par page)
    contrib_paginator = Paginator(_last_post_contrib, 6)
    contrib_page_number = request.GET.get('contrib_page')
    last_post_contrib = contrib_paginator.get_page(contrib_page_number)

    # Pagination news anciennes (6 par page)
    news_paginator = Paginator(_old_post_news, 6)
    news_page_number = request.GET.get('news_page')
    old_post_news = news_paginator.get_page(news_page_number)

    ads_header = Ad.objects.filter(active=True, position='header').order_by('?')
    ads_lateral = Ad.objects.filter(active=True, position='sidebar').order_by('?')

    context = {
        'last_post_news': last_post_news,
        'old_post_news': old_post_news,
        'last_post_contrib': last_post_contrib,
        'ads_header': ads_header,
        'ads_lateral': ads_lateral,
    }
    return render(request, 'blog/post_list.html', context)

def post_detail(request, slug):
    post = Post.objects.filter(slug=slug).first()
    comments = post.comments.all()
    category_post = Post.objects.filter(category=post.category).order_by('-created_at')[:4]

    similar_posts = Post.objects.filter(category = post.category,status='published')

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()
            return redirect('blog.post_detail', slug=slug)
    else:
        form = CommentForm()

    
    ads_header = Ad.objects.filter(active=True, position='header').order_by('?')
    ads_lateral = Ad.objects.filter(active=True, position='sidebar').order_by('?')

    context = {
        'post': post,
        'comments': comments,
        'form': form,
        'category_post':category_post,
        'similar_posts':similar_posts,
        'ads_header': ads_header,
        'ads_lateral': ads_lateral,
    }
    return render(request, 'blog/post_detail.html', context)
