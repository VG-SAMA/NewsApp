"""
Editor views for the News application.

This module contains all editor-facing views responsible for managing
articles and newsletters that belong to publishers the editor is
associated with.

Editors can:
- View all articles for their publishers
- View, update, and delete individual articles
- View, update, and delete newsletters for their publishers

All views enforce:
- User authentication
- Editor role authorization
- Object-level access control via publisher-editor relationships
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from decorators.index import editor_required
from django.http import HttpRequest
from django.contrib import messages
from helpers import index

from django.db.models import Q
from .forms import ArticleForm, EditorNewsletterForm
from .models import Article, Newsletter

route_path = 'news/editors'
redirect_path = 'editors'
helpers = index.Helpers()


"""
on get_object_pr_404, i now addded publisher__editors=request.user
"""


@login_required
@editor_required
def all_articles(request: HttpRequest):
    """
    Display all articles belonging to publishers the editor is assigned to.

    Editors can only view articles associated with publishers where they
    are listed as an editor.

    :param request: HTTP request object
    :return: Rendered dashboard with article list or redirect on error
    """

    helpers.clear_messages(request)
    query = request.GET.get('q')
    try:
        articles = Article.objects.filter(publisher__editors=request.user)
        if query:
            articles = articles.filter(
                Q(title__icontains=query)
                | Q(publisher__name__icontains=query)
                | Q(made_by_journalist=query)
            )

        return render(
            request, f'{route_path}/dashboard.html', {'articles': articles}
        )

    except Exception as e:
        messages.error(request, f'Error Occured: {e}')

    return redirect(f'news:{redirect_path}_dashboard')


@login_required
@editor_required
def view_article(request: HttpRequest, pk: int):
    """
    Display a single article for editor review.

    Access is restricted to articles that belong to a publisher
    the editor is associated with.

    :param request: HTTP request object
    :param pk: Primary key of the article
    :return: Rendered article view or redirect on error
    """

    helpers.clear_messages(request)

    try:
        article = get_object_or_404(
            Article, pk=pk, publisher__editors=request.user
        )
        if article:
            return render(
                request,
                f'{route_path}/view_article.html',
                {'article': article},
            )

        return redirect(f'news:{redirect}_view_article')

    except Exception as e:
        messages.error(request, f'Error Occured: {e}')

    return redirect(f'news:{redirect_path}_dashboard')


@login_required
@editor_required
def update_article(request: HttpRequest, pk: int):
    """
    Update an existing article.

    Editors are limited to approving or rejecting articles.
    Publisher and independence fields are preserved and hidden.

    :param request: HTTP request object
    :param pk: Primary key of the article
    :return: Rendered form or redirect after successful update
    """

    helpers.clear_messages(request)

    article = get_object_or_404(
        Article, pk=pk, publisher__editors=request.user
    )

    if request.method == 'POST':
        form = ArticleForm(request.POST, instance=article, editor=True)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Article updated successfully. If the article has been approved, the emails and tweets are being sent",
            )

            return redirect(f'news:{redirect_path}_dashboard')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = ArticleForm(instance=article, editor=True)

    return render(request, f'{route_path}/article_form.html', {'form': form})


@login_required
@editor_required
def delete_article(request: HttpRequest, pk: int):
    """
    Delete an article owned by the editor's publisher.

    Deletion is only allowed after POST confirmation.

    :param request: HTTP request object
    :param pk: Primary key of the article
    :return: Confirmation page or redirect after deletion
    """

    article = get_object_or_404(
        Article, pk=pk, publisher__editors=request.user
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


@login_required
@editor_required
def all_newsletters(request: HttpRequest):
    """
    Display all newsletters belonging to publishers the editor manages.

    :param request: HTTP request object
    :return: Rendered newsletter dashboard
    """

    user = request.user
    news = Newsletter.objects.filter(publisher__editors=user)
    query = request.GET.get('q')
    if query:
        news = news.filter(
            Q(title__icontains=query)
            | Q(journalist__username__icontains=query)
            | Q(publisher__name__icontains=query)
        )

    return render(
        request, f'{route_path}/news_dashboard.html', {'newsletters': news}
    )


@login_required
@editor_required
def view_newsletter(request: HttpRequest, pk: int):
    """
    Display a single newsletter for editor review.

    :param request: HTTP request object
    :param pk: Primary key of the newsletter
    :return: Rendered newsletter detail view
    """
    helpers.clear_messages(request)

    news = get_object_or_404(
        Newsletter, pk=pk, publisher__editors=request.user
    )

    return render(
        request, f'{route_path}/view_news.html', {'newsletter': news}
    )


@login_required
@editor_required
def update_newsletter(request: HttpRequest, pk: int):
    """
    Update an existing newsletter.

    Editors can modify the newsletter content and associated articles.

    :param request: HTTP request object
    :param pk: Primary key of the newsletter
    :return: Rendered form or redirect after successful update
    """

    helpers.clear_messages(request)

    newsletter = get_object_or_404(
        Newsletter.objects.prefetch_related('articles'),
        pk=pk,
        publisher__editors=request.user,
    )

    if request.method == "POST":
        form = EditorNewsletterForm(request.POST, instance=newsletter)
        if form.is_valid():
            form.save()
            messages.success(request, "Newsletter updated successfully.")
            return redirect(f'news:{redirect_path}_news_dashboard')
    else:
        form = EditorNewsletterForm(instance=newsletter)

    return render(
        request,
        f'{route_path}/news_form.html',
        {
            'form': form,
            'newsletter': newsletter,
        },
    )


@login_required
@editor_required
def delete_newsletter(request: HttpRequest, pk: int):
    """
    Delete a newsletter owned by the editor's publisher.

    Deletion requires POST confirmation.

    :param request: HTTP request object
    :param pk: Primary key of the newsletter
    :return: Confirmation page or redirect after deletion
    """

    helpers.clear_messages(request)
    news = get_object_or_404(
        Newsletter, pk=pk, publisher__editors=request.user
    )

    if request.method == 'POST':

        try:
            news.delete()
            messages.success(request, 'Newsletter deleted successfully :)')

        except Exception as e:
            messages.error(request, f'Error Occurred: {e}')

        return redirect(f'news:{redirect_path}_news_dashboard')

    return render(
        request, f'{route_path}/news_confirm_delete.html', {'news': news}
    )
