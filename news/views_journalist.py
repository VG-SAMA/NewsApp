"""
Journalist views for the News application.

This module contains all view logic related to journalists, including
creating, reading, updating, and deleting articles and newsletters.

Access to all views in this module is restricted to authenticated users
with the journalist role. Object-level permissions are enforced using
filtered `get_object_or_404` queries to ensure journalists may only
interact with their own content.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from decorators.index import journalist_required
from django.http import HttpRequest, HttpResponseForbidden
from django.contrib import messages
from helpers import index
from django.db.models import Q
from .forms import ArticleForm, NewsletterForm
from .models import Article, Newsletter

route_path = 'news/journalists'
redirect_path = 'journalists'
helpers = index.Helpers()

"""
on get_object_pr_404, i now addded made_by_journalist=request.user
"""


@login_required
@journalist_required
def create_article(request: HttpRequest):
    """
    Handles the creation of a new article by a journalist.

    GET: Renders an empty ArticleForm.
    POST: Validates the form and saves the article with the
          logged-in journalist as the author.

    Args:
        request (HttpRequest): The incoming HTTP request.

    Returns:
        HttpResponse: Rendered form template or redirect to dashboard
                      on successful creation.
    """

    helpers.clear_messages(request)

    user = request.user
    if request.method == "POST":

        form = ArticleForm(request.POST, user=user)

        if form.is_valid():
            article = form.save(commit=False)
            article.made_by_journalist = user

            try:
                article.save()
                helpers.clear_messages(request)
                messages.success(request, "Article created successfully!")
                return redirect(f"news:{redirect_path}_dashboard")

            except Exception as e:
                helpers.clear_messages(request)
                messages.error(request, f"Error saving article: {e}")
    else:
        form = ArticleForm(user=user)

    return render(
        request,
        f'{route_path}/article_form.html',
        {'form': form},
    )


@login_required
@journalist_required
def read_articles(request: HttpRequest):
    """
    Display a list of articles created by the logged-in journalist.

    Supports optional text-based searching via query parameters.

    Args:
        request (HttpRequest): Incoming HTTP request.

    Returns:
        HttpResponse: Rendered dashboard with filtered article list.
    """

    helpers.clear_messages(request)

    user = request.user
    query = request.GET.get('q')
    articles = Article.objects.filter(made_by_journalist=user)

    if query:
        articles = articles.filter(
            Q(title__icontains=query)
            | Q(content__icontains=query)
            | Q(publisher__name__icontains=query)
        )

    return render(
        request, f'{route_path}/dashboard.html', {'articles': list(articles)}
    )


@login_required
@journalist_required
def view_article(request: HttpRequest, pk: int):
    """
    Displays a single article to the journalist if they are the author.

    Args:
        request (HttpRequest): The incoming HTTP request.
        pk (int): Primary key of the Article to view.

    Returns:
        HttpResponse: Rendered article view template.
        HttpResponseForbidden if user tries to access another journalist's article.
    """

    helpers.clear_messages(request)

    article = get_object_or_404(
        Article, pk=pk, made_by_journalist=request.user
    )
    if article:
        return render(
            request, f'{route_path}/view_article.html', {'article': article}
        )

    return redirect(f'news:{redirect}_view_article')


@login_required
@journalist_required
def update_article(request: HttpRequest, pk: int):
    """
    Updates an article authored by the logged-in journalist.

    GET: Renders ArticleForm prefilled with existing data.
    POST: Validates the form and updates the article.
          If linked to a publisher, resets approval and independent flags.

    Args:
        request (HttpRequest): The incoming HTTP request.
        pk (int): Primary key of the Article to update.

    Returns:
        HttpResponse: Rendered form template or redirect to dashboard on success.
    """

    helpers.clear_messages(request)

    article = get_object_or_404(
        Article, pk=pk, made_by_journalist=request.user
    )

    if request.method == 'POST':
        form = ArticleForm(request.POST, instance=article, user=request.user)

        if form.is_valid():
            try:
                this_article = form.save(commit=False)

                if this_article.publisher:
                    this_article.is_approved = False
                    this_article.is_independant = False

                this_article.save()
                messages.success(request, 'Article updated successfully')
                return redirect(f'news:{redirect_path}_dashboard')

            except Exception as e:
                messages.error(request, f'Error Occurred: {e}')
                return redirect(f'news:{redirect_path}_dashboard')
    else:
        form = ArticleForm(instance=article, user=request.user)

    return render(request, f'{route_path}/article_form.html', {'form': form})


@login_required
@journalist_required
def delete_article(request: HttpRequest, pk: int):
    """
    Delete an article owned by the logged-in journalist.

    Args:
        request (HttpRequest): Incoming HTTP request.
        pk (int): Primary key of the article.

    Returns:
        HttpResponse: Confirmation page or redirect after deletion.
    """
    helpers.clear_messages(request)

    article = get_object_or_404(
        Article, pk=pk, made_by_journalist=request.user
    )

    if request.method == 'POST':
        try:
            article.delete()
            messages.success(request, 'Article has been deleted')
        except Exception as e:
            messages.error(request, f'Error Occurred: {e}')

        return redirect(f'news:{redirect_path}_dashboard')

    return render(
        request, f'{route_path}/confirm_delete.html', {'article': article}
    )


# neswlewtte logic
@login_required
@journalist_required
def create_newsletter(request: HttpRequest):
    """
    Create a new newsletter for the logged-in journalist.

    Args:
        request (HttpRequest): Incoming HTTP request.

    Returns:
        HttpResponse: Rendered form or redirect to newsletter dashboard.
    """

    helpers.clear_messages(request)

    if request.method == "POST":
        form = NewsletterForm(request.POST, user=request.user)
        if form.is_valid():
            newsletter = form.save(commit=False)
            newsletter.journalist = request.user
            newsletter.save()
            form.save_m2m()
            return redirect('news:journalists_news_dashboard')
    else:
        form = NewsletterForm(user=request.user)

    # Initially show only the logged-in journalist's independent articles
    articles = Article.objects.filter(is_approved=True).filter(
        Q(is_independant=True, made_by_journalist=request.user)
        | Q(is_independant=False, publisher__isnull=False)
    )

    return render(
        request,
        f'{route_path}/news_form.html',
        {"form": form, "articles": articles},
    )


@login_required
@journalist_required
def newsletter_dashboard(request: HttpRequest):
    """
    Display all newsletters created by the logged-in journalist.

    Supports optional search filtering.

    Args:
        request (HttpRequest): Incoming HTTP request.

    Returns:
        HttpResponse: Rendered newsletter dashboard.
    """
    helpers.clear_messages(request)

    newsletters = (
        Newsletter.objects.filter(journalist=request.user)
        .prefetch_related('articles')
        .order_by('-created_at')
    )

    query = request.GET.get('q')

    if query:
        newsletters = newsletters.filter(
            Q(title__icontains=query) | Q(publisher__name__icontains=query)
        )

    return render(
        request,
        f'{route_path}/news_dashboard.html',
        {'newsletters': newsletters},
    )


@login_required
@journalist_required
def view_newsletter(request: HttpRequest, pk: int):
    """
    Display a single newsletter owned by the logged-in journalist.

    Args:
        request (HttpRequest): Incoming HTTP request.
        pk (int): Primary key of the newsletter.

    Returns:
        HttpResponse: Rendered newsletter view.
    """
    helpers.clear_messages(request)

    newsletter = get_object_or_404(
        Newsletter.objects.prefetch_related(
            'articles', 'articles__made_by_journalist'
        ),
        pk=pk,
        journalist=request.user,
    )
    if newsletter.journalist != request.user:
        return HttpResponseForbidden("You cannot view this newsletter.")

    return render(
        request,
        f'{route_path}/view_news.html',
        {'newsletter': newsletter},
    )


@login_required
@journalist_required
def update_newsletter(request: HttpRequest, pk: int):
    """
    Update an existing newsletter owned by the logged-in journalist.

    Args:
        request (HttpRequest): Incoming HTTP request.
        pk (int): Primary key of the newsletter.

    Returns:
        HttpResponse: Rendered form or redirect on success.
    """
    helpers.clear_messages(request)

    newsletter = get_object_or_404(Newsletter, pk=pk, journalist=request.user)

    if request.method == "POST":
        form = NewsletterForm(
            request.POST, instance=newsletter, user=request.user
        )
        if form.is_valid():
            form.save()
            return redirect('news:journalists_news_dashboard')
    else:
        form = NewsletterForm(instance=newsletter, user=request.user)

    # Filter articles based on newsletter type
    if newsletter.is_independant:
        articles = Article.objects.filter(
            made_by_journalist=request.user, is_approved=True
        )
    else:
        articles = Article.objects.filter(
            publisher=newsletter.publisher, is_approved=True
        )

    return render(
        request,
        f'{route_path}/news_form.html',
        {"form": form, "articles": articles, "newsletter": newsletter},
    )


@login_required
@journalist_required
def delete_newsletter(request: HttpRequest, pk: int):
    """
    Delete a newsletter owned by the logged-in journalist.

    Args:
        request (HttpRequest): Incoming HTTP request.
        pk (int): Primary key of the newsletter.

    Returns:
        HttpResponse: Confirmation page or redirect after deletion.
    """

    helpers.clear_messages(request)

    news = get_object_or_404(Newsletter, pk=pk, journalist=request.user)

    if request.method == 'POST':
        try:
            news.delete()

        except Exception as e:
            messages.error(request, f'Error Occurred: {e}')

        return redirect(f'news:{redirect_path}_news_dashboard')

    return render(
        request, f'{route_path}/news_confirm_delete.html', {'news': news}
    )
