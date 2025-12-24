"""
Reader views for the News application.

This module provides functionality for authenticated readers to:
- View articles based on their subscriptions
- Search articles and newsletters
- View individual articles and newsletters
- Manage publisher and journalist subscriptions

Access to all views is restricted to users with the `reader` role.
Content visibility is determined by the reader's active subscriptions.
"""

from django.shortcuts import render, redirect, get_object_or_404
from decorators.index import reader_required
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from .models import Article, Newsletter
from django.db.models import Q
from helpers import index
from django.contrib import messages
from .forms import ReaderSubscriptionForm

route_path = 'news/readers'
redirect_path = 'readers'
helpers = index.Helpers()


@login_required
@reader_required
def get_all_articles(request: HttpRequest):
    """
    Display all articles available to the logged-in reader.

    Articles are filtered based on the reader's subscriptions:
    - Publisher articles from subscribed publishers
    - Independent articles from subscribed journalists

    Supports optional search functionality by article title
    or journalist name.

    :param request: HTTP request object
    :return: Rendered article dashboard
    """

    user = request.user
    query = request.GET.get('q')

    all_articles = (
        Article.objects.filter(is_approved=True)
        .filter(
            Q(
                is_independant=False,
                publisher__in=user.reader_publisher_subscriptions.all(),  # type: ignore
            )
            | Q(
                is_independant=True,
                made_by_journalist__in=user.reader_journalist_subscriptions.all(),  # type: ignore
            )
        )
        .distinct()
    )

    if query:
        all_articles = all_articles.filter(
            Q(title__icontains=query)
            | Q(made_by_journalist__username__icontains=query)
            | Q(made_by_journalist__first_name__icontains=query)
            | Q(made_by_journalist__last_name__icontains=query)
        )

    return render(
        request, f'{route_path}/dashboard.html', {'articles': all_articles}
    )


@login_required
@reader_required
def view_article(request: HttpRequest, pk: int):
    """
    Display a single article to the reader.

    Access is allowed only if the article exists. Subscription
    checks are enforced at the listing level.

    :param request: HTTP request object
    :param pk: Primary key of the article
    :return: Rendered article detail view
    """

    helpers.clear_messages(request)

    article = get_object_or_404(Article, pk=pk)

    try:
        return render(
            request, f'{route_path}/view_article.html', {'article': article}
        )

    except Exception as e:
        messages.error(request, f'Error Occurred: {e}')
        return redirect(f'news:{redirect_path}_dashboard')


@login_required
@reader_required
def all_newsletters(request: HttpRequest):
    """
    Display all newsletters available to the reader.

    Newsletters are filtered based on the reader's subscriptions:
    - Publisher newsletters from subscribed publishers
    - Independent newsletters from subscribed journalists

    Supports optional search functionality by title or journalist name.

    :param request: HTTP request object
    :return: Rendered newsletter dashboard
    """

    helpers.clear_messages(request)

    user = request.user
    query = request.GET.get('q')

    newsletters = (
        Newsletter.objects.filter(
            Q(
                is_independant=False,
                publisher__in=user.reader_publisher_subscriptions.all(),  # type: ignore
            )
            | Q(
                is_independant=True,
                journalist__in=user.reader_journalist_subscriptions.all(),  # type: ignore
            )
        )
        .select_related("journalist", "publisher")
        .prefetch_related("articles")
        .distinct()
    )

    if query:
        newsletters = newsletters.filter(
            Q(title__icontains=query)
            | Q(journalist__username__icontains=query)
            | Q(journalist__first_name__icontains=query)
            | Q(journalist__last_name__icontains=query)
        )

    return render(
        request,
        f'{route_path}/news_dashboard.html',
        {'newsletters': newsletters},
    )


@login_required
@reader_required
def view_newsletter(request: HttpRequest, pk: int):
    """
    Display a single newsletter to the reader.

    :param request: HTTP request object
    :param pk: Primary key of the newsletter
    :return: Rendered newsletter detail view
    """

    helpers.clear_messages(request)

    news = get_object_or_404(Newsletter, pk=pk)

    try:
        return render(
            request, f'{route_path}/view_news.html', {'newsletter': news}
        )

    except Exception as e:
        messages.error(request, f'Error Occurred: {e}')
        return redirect(f'news:{redirect_path}_news_dashboard')


@login_required
@reader_required
def manage_subscriptions(request: HttpRequest):
    """
    Manage reader subscriptions to publishers and journalists.

    Allows the reader to subscribe or unsubscribe from available
    publishers and journalists using a single form.

    :param request: HTTP request object
    :return: Rendered subscription form or redirect on success
    """

    helpers.clear_messages(request)

    user = request.user

    if request.method == "POST":
        form = ReaderSubscriptionForm(request.POST, instance=user)  # type: ignore

        if form.is_valid():
            form.save()
            messages.success(
                request, 'Your subscriptions were updated successfully.'
            )
            return redirect(f'news:{redirect_path}_dashboard')
    else:
        form = ReaderSubscriptionForm(instance=user)  # type: ignore

    return render(
        request,
        f"{route_path}/subscriptions_form.html",
        {"form": form},
    )
