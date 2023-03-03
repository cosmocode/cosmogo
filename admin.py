import json

from typing import Type

from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.db.models import Model
from django.http import Http404
from django.urls import reverse
from django.utils.html import format_html

from cosmogo.utils.gettext import trans

DEFAULT_LINK_TEMPLATE = '<a href="{url}">{label}</a>'


def admin_url(model: Type[Model], view: str, *args, site=None, **kwargs) -> str:
    """
    Return an url to an admin view.
    """

    opts = model._meta
    site = site or admin.site
    info = site.name, opts.app_label, opts.model_name, view

    return reverse('%s:%s_%s_%s' % info, args=args, kwargs=kwargs)


def admin_link(obj: Model, view='change', site=None, label=None, template=DEFAULT_LINK_TEMPLATE):
    url = admin_url(type(obj), view, obj.pk, site=site)

    return format_html(template, url=url, obj=obj, label=label or obj)


def json_display(data):
    content = json.dumps(data, indent=2)

    return format_html('<pre style="padding: 0">{content}</pre>', content=content)


class DefaultTabularInline(admin.TabularInline):
    template = 'admin/inline/tabular-without-original.html'
    extra = 0


class AdminViewMixin:

    def get_object_for(self: admin.ModelAdmin, permission: str, request, object_id):
        obj = self.get_object(request, object_id)

        if not getattr(self, f'has_{permission}_permission')(request, obj=obj):
            raise PermissionDenied

        if obj is None:
            msg = trans('%(name)s object with primary key %(key)r does not exist.')
            context = {'name': self.opts.verbose_name, 'key': object_id}

            raise Http404(msg % context)

        return obj

    def get_object_for_change(self, request, object_id):
        return self.get_object_for('change', request, object_id)

    def get_object_for_delete(self, request, object_id):
        return self.get_object_for('delete', request, object_id)


class ReadOnlyAdminMixin:

    def has_add_permission(self, request, obj=None):
        # For `InlineModelAdmin` the parent object may be passed via `obj`.
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class ReadOnlyModelAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    """
    Immutable admin for a given model.
    """
