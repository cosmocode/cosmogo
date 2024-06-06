"""
Module contains common view mixins.
"""

import logging

try:
    from http.client import responses
except ImportError:
    from httplib import responses

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.http import Http404, HttpResponse, JsonResponse

from .encoder import AdvancedJSONEncoder


class APIViewMixIn(object):
    """
    A mixin for views that should return a JSON response.
    """

    DEBUG = settings.DEBUG
    encoder = AdvancedJSONEncoder
    logger = logging.getLogger(__name__)

    @classmethod
    def evaluate(cls, data=None, success=True, message=None, code=None):
        """
        Evaluate and validate the given parameters and return suitable defaults for missing ones.
        """

        try:
            assert (data is None or isinstance(data, dict)), 'data should be a dictionary'
            assert isinstance(success, bool), 'success should be a boolean'
            assert code is None or isinstance(code, int), 'code should be an integer'
        except AssertionError as error:
            return cls.server_error(
                'A view inheriting from %s should return a tuple consisting of a data dictionary, '
                'a status code integer and a boolean success flag. %s did not: %s.',
                APIViewMixIn.__name__, cls.__name__, error
            )

        data = data or {}
        code = code or {True: 200, False: 400}.get(success)
        message = getattr(message, 'message', message) or responses.get(code, message)

        return data, success, message, code

    def dispatch(self, request, *args, **kwargs):
        """
        Processes the views response and returns a JSON response if possible.
        """

        try:
            response = super(APIViewMixIn, self).dispatch(request, *args, **kwargs)
        except PermissionDenied as error:
            data, success, message, code = self.evaluate(success=False, message=f'{error}', code=403)
        except Http404 as error:
            data, success, message, code = self.evaluate(success=False, message=f'{error}', code=404)
        except NotImplementedError:
            return self.http_method_not_allowed(request, *args, **kwargs)
        except Exception as error:
            data, success, message, code = self.server_error('Internal Server Error: %s', error, error=error)
        else:
            if response is None:
                data, success, message, code = self.evaluate(data=response)
            elif isinstance(response, bool):
                data, success, message, code = self.evaluate(success=response)
            elif isinstance(response, int) and 100 <= response < 700:
                data, success, message, code = self.evaluate(success=response < 400, code=response)
            elif isinstance(response, tuple):
                data, success, message, code = self.evaluate(*response)
            elif isinstance(response, dict):
                data, success, message, code = self.evaluate(data=response)
            elif isinstance(response, HttpResponse):
                return response
            else:
                data, success, message, code = self.server_error(
                    'A view inheriting from %s should return a tuple, a dict or a HttpResponse. %s did return %s.',
                    APIViewMixIn.__name__, self.__class__.__name__, response.__class__.__name__
                )

        return self.respond(data, success, message, code)

    def respond(self, data, success, message, code):
        """
        Returns given data as a JSON response and merges in the success status and the message.
        """

        return JsonResponse(
            data=dict({'success': success, 'message': message}, **data),
            encoder=self.encoder,
            status=code,
        )

    @classmethod
    def server_error(cls, msg, *args, error=None):
        if cls.DEBUG:
            if error:
                raise
            else:
                raise ImproperlyConfigured(msg % args)

        if error:
            cls.logger.exception(msg, *args, exc_info=error)
        else:
            cls.logger.error(msg, *args)

        return cls.evaluate(success=False, message=f'{error}', code=500)


APIViewMixin = APIViewMixIn
