"""
Twitter Posting Module

This module contains two classes for posting tweets to Twitter:
TwitterAutomation - Implements a singleton class that uses OAuth1 tokens for automatic posting
   without user interaction after the first authentication.

⚠ NOTE: The Twitter account used in this project has been suspended. To test posting functionality,
you must replace the consumer key, consumer secret, access token, and access token secret with
your own valid credentials from the Twitter developer portal.
"""

from requests_oauthlib import OAuth1Session
import os
import certifi
import os
import json


def clear_screen():
    os.system("cls")


CONSUMER_KEY = ""
CONSUMER_SECRET = ""

ACCESS_KEY = ""
ACCESS_SECRET = ""

BEARER_TOKEN = ""

CLIENT_ID = ""
CLIENT_SECRET = ""


class TwitterAutomation:
    """
    Singleton Twitter posting class.

    Handles automatic tweet posting without console interaction.
    Only one instance of this class exists during runtime.
    Requires valid OAuth1 tokens (ACCESS_KEY and ACCESS_SECRET).

    Methods:
    - make_tweet(text, media_id=None): Posts a tweet, optionally with media.
    - create_image(file_path): Uploads an image and returns its media_id for tweeting.
    """

    _instance = None
    _oauth = None

    def __new__(cls, *args, **kwargs):
        """Ensure only one instance exists (Singleton pattern)."""

        if cls._instance is None:
            cls._instance = super(TwitterAutomation, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the OAuth1 session with access tokens."""

        self.oauth = OAuth1Session(
            CONSUMER_KEY,
            client_secret=CONSUMER_SECRET,
            resource_owner_key=ACCESS_KEY,
            resource_owner_secret=ACCESS_SECRET,
        )

    def make_tweet(self, text, media_id=None):
        """
        Post a tweet.

        Args:
            text (str): The tweet text.
            media_id (str, optional): ID of media uploaded to attach to the tweet.

        Returns:
            dict: JSON response from Twitter API.
        """

        payload = {"text": text}
        if media_id:
            payload["media"] = {"media_ids": [media_id]}

        response = self.oauth.post(
            "https://api.twitter.com/2/tweets",
            json=payload,
            verify=certifi.where(),
        )

        if response.status_code != 201:
            clear_screen()
            raise Exception(
                f"Error Occurred: {response.status_code}, {response.text}"
            )

        json_response = response.json()
        print(json.dumps(json_response, indent=4, sort_keys=True))
        return json_response

    def create_image(self, file_path: str):
        """
        Upload an image to Twitter and return the media ID.

        Args:
            file_path (str): Path to the local image file.

        Returns:
            str: Media ID string for attaching to a tweet.
        """

        with open(file_path, "rb") as img:
            response = self.oauth.post(
                "https://upload.twitter.com/1.1/media/upload.json",
                files={"media": img},
            )

        if response.status_code != 200:
            clear_screen()
            raise Exception(
                f"Image upload failed: {response.status_code}, {response.text}"
            )

        post_img = response.json()
        return post_img["media_id_string"]
