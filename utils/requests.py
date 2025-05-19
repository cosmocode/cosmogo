import shutil

from pathlib import Path

from requests import Session, RequestException, api
from requests.auth import AuthBase

from .tempdir import maketempdir


class TokenAuth(AuthBase):
    keyword = 'Token'

    def __init__(self, token, keyword=None):
        self.token = token
        self.keyword = keyword or self.keyword

    def __call__(self, request):
        request.headers['Authorization'] = f'{self.keyword} {self.token}'
        return request


class BearerAuth(TokenAuth):
    keyword = 'Bearer'


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


def download(url: str, destination: Path, *, session=api):
    with maketempdir(prefix=destination.stem) as tempdir:
        source = tempdir / destination.name

        with open(source, 'wb') as tmp:
            with session.get(url, stream=True) as response:
                response.raise_for_status()

                for chunk in response.iter_content(chunk_size=None):
                    tmp.write(chunk)

        return shutil.move(source, destination)
