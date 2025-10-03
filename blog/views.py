from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from .models import Comment, Post
from .forms import CommentForm
from django.core.paginator import Paginator
from backoffice.models import Ad
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from users.models import Notification
from django.urls import reverse
from django.http import JsonResponse


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

    print(post.author)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()


             # 🔔 Notifier l’auteur du post (sauf si c’est lui qui commente)
            if post.author != request.user:
                Notification.objects.create(
                    recipient=post.author,
                    type="info",
                    message=f"{request.user.first_name} {request.user.last_name} a commenté votre article : {post.title}",
                    url=f"/blog/post/{post.slug}/"
                )

            # 🔔 Notifier les autres commentateurs uniques (sauf l'auteur du commentaire actuel)
            other_commenters = (
                Comment.objects.filter(post=post)
                .exclude(user=request.user)  # pas l'auteur du commentaire actuel
                .values_list("user", flat=True)
                .distinct()
            )

            for user_id in other_commenters:
                if user_id != post.author.id:  # éviter double notif à l'auteur déjà notifié
                    Notification.objects.create(
                        recipient_id=user_id,
                        type="info",
                        message=f"{request.user.first_name} {request.user.last_name} a aussi commenté l'article : {post.title}",
                        url=f"/blog/post/{post.slug}/"
                    )
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


@login_required
def comment_edit(request, pk):
    comment = get_object_or_404(Comment, pk=pk)

    if comment.user != request.user:
        messages.error(request, "Vous n'avez pas la permission de modifier ce commentaire.")
        return redirect('blog.post_detail', slug=comment.post.slug)

    if request.method == 'POST':
        new_content = request.POST.get('content')
        if new_content:
            comment.content = new_content
            comment.save()
            messages.success(request, "Votre commentaire a été modifié avec succès.")
    return redirect('blog.post_detail', slug=comment.post.slug)



@login_required
def comment_delete(request, pk):
    comment = get_object_or_404(Comment, pk=pk)

    if comment.user != request.user:
        messages.error(request, "Vous n'avez pas la permission de supprimer ce commentaire.")
        return redirect('blog.post_detail', slug=comment.post.slug)

    if request.method == 'POST':
        comment.delete()
        messages.success(request, "Votre commentaire a été supprimé avec succès.")
        return redirect('blog.post_detail', slug=comment.post.slug)

    return redirect('blog.post_detail', slug=comment.post.slug)



def share_post(request, slug, platform):
    post = get_object_or_404(Post, slug=slug)

    # Incrémente le compteur de partage
    post.shares += 1
    post.save(update_fields=["shares"])

    post_url = request.build_absolute_uri(reverse("blog.post_detail", args=[post.slug]))

    # Redirection selon la plateforme choisie
    if platform == "facebook":
        return redirect(f"https://www.facebook.com/sharer/sharer.php?u={post_url}")
    elif platform == "twitter":
        return redirect(f"https://twitter.com/intent/tweet?url={post_url}&text={post.title}")
    elif platform == "whatsapp":
        return redirect(f"https://api.whatsapp.com/send?text={post.title} - {post_url}")
    elif platform == "linkedin":
        return redirect(f"https://www.linkedin.com/sharing/share-offsite/?url={post_url}")
    
    return redirect(post_url)  # fallback