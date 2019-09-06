import os

from django.contrib.staticfiles.storage import StaticFilesStorage

from cosmogo.utils.webpack import get_asset


class WebPackStorage(StaticFilesStorage):
    """
    A static file storage that could map webpack
    bundles to their hash named url's.
    """

    def url(self, name):
        """
        Try to look up the name in the webpack stats file
        and return the url containing the current hash.
        """

        filename = os.path.basename(name)

        try:
            chunk, suffix, extension = filename.split('.')
        except ValueError:
            pass
        else:
            name = get_asset(chunk, extension) or name

        return super(WebPackStorage, self).url(name)
