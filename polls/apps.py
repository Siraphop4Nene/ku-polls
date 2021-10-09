"""Apps for ku-polls."""
from django.apps import AppConfig


class PollsConfig(AppConfig):
    """Class for PollsConfig."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'polls'
