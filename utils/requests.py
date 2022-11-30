from requests import Session, RequestException


class BaseTimeOutSession(Session):

    def __init__(self, timeout):
        self.timeout = timeout

        super(BaseTimeOutSession, self).__init__()

    def request(self, *args, **kwargs):
        kwargs.setdefault('timeout', self.timeout)

        return super(BaseTimeOutSession, self).request(*args, **kwargs)

    def json(self, method, url, **kwargs):
        try:
            response = self.request(method, url, **kwargs)
        except RequestException as error:
            return None, error

        if response and not (response.status_code == 204):
            return response, response.json()

        return response, None


class TimeOutSession(BaseTimeOutSession):

    def json(self, method, url, **kwargs):
        response, data = super(TimeOutSession, self).json(method, url, **kwargs)

        if response is None:
            return None, data
        elif response:
            return True, data
        else:
            return False, response
