from django.apps import AppConfig


class NewsConfig(AppConfig):
    name = 'news'

    def ready(self) -> None:
        """
        Docstring for ready function when applications starts
        
        :param self: self
        
        :returns: None
        
        """

        import news.signals  # type: ignore
