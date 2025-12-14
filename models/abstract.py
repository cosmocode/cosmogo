import datetime

from django.db import models
from django.utils import timezone
from django.utils.timezone import localtime
from django.utils.translation import gettext_lazy as _

from cosmogo.utils.migrations import disable_auto_now


class UpdateQuerySet(models.QuerySet):

    def get_for_update(self, *, nowait=False, skip_locked=False, of=(), no_key=False, **kwargs):
        return self.select_for_update(nowait=nowait, skip_locked=skip_locked, of=of, no_key=no_key).get(**kwargs)


class UpdateModel(models.Model):
    objects = UpdateQuerySet.as_manager()

    class Meta:
        abstract = True

    def update(self, *, using=None, **values):
        for field, value in values.items():
            setattr(self, field, value)

        return self.save(update_fields=[*values], using=using)


class Timestamped(UpdateModel):
    created = models.DateTimeField(_('created'), default=timezone.now, editable=False)
    modified = models.DateTimeField(_('modified'), auto_now=True)

    TIMESTAMP_FIELDS = [
        'created',
        'modified',
    ]

    class Meta:
        abstract = True

    def update(self, *, using=None, modified: datetime.datetime | bool = None, **values):
        if modified in (None, True):
            values['modified'] = localtime(None)
        elif isinstance(modified, datetime.datetime):
            values['modified'] = modified

        with disable_auto_now(self.__class__, 'modified'):
            return super().update(using=using, **values)
