"""
Module contains common view mixins.
"""

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
            if cls.DEBUG:
                raise ImproperlyConfigured(
                    'A view inherting from %s should return a tuple consisting of a data dictionary, '
                    'a status code integer and a boolean success flag. %s did not: %s.' % (
                        APIViewMixIn.__name__,
                        cls.__name__,
                        error
                    )
                )
            else:
                return {}, False, responses.get(500), 500

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
            data, success, message, code = self.evaluate(success=False, message=error, code=403)
        except Http404 as error:
            data, success, message, code = self.evaluate(success=False, message=error, code=404)
        except NotImplementedError:
            return self.http_method_not_allowed(request, *args, **kwargs)
        except Exception as error:
            if self.DEBUG:
                raise
            else:
                data, success, message, code = self.evaluate(success=False, message=error, code=500)
        else:
            if response is None:
                data, success, message, code = self.evaluate(data=response)
            elif isinstance(response, bool):
                data, success, message, code = self.evaluate(success=response)
            elif isinstance(response, int) and 100 <= response < 700:
                data, success, message, code = self.evaluate(code=response)
            elif isinstance(response, tuple):
                data, success, message, code = self.evaluate(*response)
            elif isinstance(response, dict):
                data, success, message, code = self.evaluate(data=response)
            elif isinstance(response, HttpResponse):
                return response
            elif self.DEBUG:
                raise ImproperlyConfigured(
                    'A view inherting from %s should return a tuple, '
                    'a dict or a HttpResponse. %s did return %s.' % (
                        APIViewMixIn.__name__,
                        self.__class__.__name__,
                        response.__class__.__name__,
                    )
                )
            else:
                data, success, message, code = self.evaluate(success=False, code=500)

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
