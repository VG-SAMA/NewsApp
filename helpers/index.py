import os, platform
from django.http import HttpRequest
from django.contrib import messages


class Helpers:
    def clear_screen(self):
        """Function to clear request messages so any messages are only new messages."""
        if platform.system() == 'Windows':
            os.system('clear all')
        else:
            os.system('clear')

    def clear_messages(self, request: HttpRequest):
        """Function to clear the messages from request."""
        list(messages.get_messages(request))
