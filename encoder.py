from django.core.serializers.json import DjangoJSONEncoder
from django.utils.encoding import force_text
from django.utils.functional import Promise


class AdvancedJSONEncoder(DjangoJSONEncoder):
    """
    Advanced JSON encoder that could handle common
    data types when working with django.
    """

    def default(self, o):
        """
        Converts exceptions and promises to strings.
        """

        if isinstance(o, (Exception, Promise)):
            return force_text(o)

        return super(AdvancedJSONEncoder, self).default(o)
