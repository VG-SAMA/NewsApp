"""
Publisher management views for the News application.

This module provides manager-level functionality for creating,
viewing, updating, and deleting publishers.

Access is restricted to authenticated users with the
`manager_publishers` role.

This functionality was not required, however it makes it a bit easier for the user
to create and manage the publishers without going into the admin site.
However creating a superuser will be needed to access this part of the application.


Managers can:
- Create new publishers
- View all publishers
- Search publishers by name or description
- View publisher details
- Update publisher information
- Delete publishers
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from decorators.index import manager_publishers_required
from django.http import HttpRequest
from django.contrib import messages
from helpers import index
from django.db.models import Q
from .forms import PublisherForm
from .models import Publisher

route_path = 'news/admins'

helpers = index.Helpers()


@login_required
@manager_publishers_required
def create_publisher(request: HttpRequest):
    """
    Create a new publisher.

    Validates uniqueness of the publisher name before saving.
    If a publisher with the same name already exists, an error
    message is displayed and the form is re-rendered.

    :param request: HTTP request object
    :return: Rendered form or redirect to publisher list on success
    """

    helpers.clear_messages(request)

    if request.method == 'POST':
        form = PublisherForm(request.POST)

        if form.is_valid():
            name = form.cleaned_data['name']
            if Publisher.objects.filter(name=name).exists():
                messages.error(
                    request,
                    f"A publisher with the name '{name}' already exists.",
                )
                # keep the form with data
                return render(
                    request,
                    f'{route_path}/publisher_form.html',
                    {'form': form},
                )

            try:
                form.save()
                messages.success(
                    request, f"Publisher '{name}' created successfully!"
                )
                return redirect('news:all_publishers')
            except Exception as e:
                messages.error(request, f'Error occurred: {e}')
                # keep the form with itss data
                return render(
                    request,
                    f'{route_path}/publisher_form.html',
                    {'form': form},
                )

        else:
            # form has validation errors, just render it
            return render(
                request, f'{route_path}/publisher_form.html', {'form': form}
            )

    # New form returneds
    form = PublisherForm()
    return render(request, f'{route_path}/publisher_form.html', {'form': form})


@login_required
@manager_publishers_required
def read_publishers(request: HttpRequest):
    """
    Display a list of all publishers.

    Supports optional search functionality using query parameters
    to filter publishers by name or description.

    :param request: HTTP request object
    :return: Rendered publisher list view
    """

    all_pubs = Publisher.objects.all()
    query = request.GET.get('q', None)

    if query:
        all_pubs = all_pubs.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    return render(
        request, f'{route_path}/view_publishers.html', {'pubs': all_pubs}
    )


@login_required
@manager_publishers_required
def publisher_details(request: HttpRequest, pk: int):
    """
    Display detailed information for a single publisher.

    :param request: HTTP request object
    :param pk: Primary key of the publisher
    :return: Rendered publisher detail page or redirect if not found
    """

    helpers.clear_messages(request)

    this_pub = get_object_or_404(Publisher, pk=pk)
    if this_pub:
        return render(
            request, f'{route_path}/publisher_details.html', {'pub': this_pub}
        )

    messages.error(request, 'Publisher could not be found')
    return redirect('news:all_publishers')


@login_required
@manager_publishers_required
def update_publisher(request: HttpRequest, pk: int):
    """
    Update an existing publisher.

    :param request: HTTP request object
    :param pk: Primary key of the publisher
    :return: Rendered form or redirect after successful update
    """

    helpers.clear_messages(request)
    pub = get_object_or_404(Publisher, pk=pk)

    if request.method == 'POST':
        form = PublisherForm(request.POST, instance=pub)

        if form.is_valid():
            try:
                form.save()
                return redirect('news:all_publishers')

            except Exception as e:
                messages.error(request, f'Error Occurred: {e}')
                return redirect('news:all_publishers')
    else:
        form = PublisherForm(instance=pub)

    return render(request, f'{route_path}/publisher_form.html', {'form': form})


@login_required
@manager_publishers_required
def delete_publisher(request: HttpRequest, pk: int):
    """
    Delete a publisher.

    Deletion requires POST confirmation to prevent accidental removal.

    :param request: HTTP request object
    :param pk: Primary key of the publisher
    :return: Confirmation page or redirect after deletion
    """

    helpers.clear_messages(request)

    this_pub = get_object_or_404(Publisher, pk=pk)

    if request.method == 'POST':
        try:
            this_pub.delete()
            messages.success(request, 'Publishers has been deleted')
        except Exception as e:
            messages.error(request, f'Error Occurred: {e}')

        return redirect('news:all_publishers')

    return render(
        request, f'{route_path}/confirm_delete.html', {'pub': this_pub}
    )
