from django.apps import AppConfig


class NewsConfig(AppConfig):
    name = 'news'

    def ready(self) -> None:
        import news.signals  # type: ignore
