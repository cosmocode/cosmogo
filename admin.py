from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.db.models import Model
from django.http import Http404
from django.utils.safestring import mark_safe

from cosmogo.utils.gettext import trans
from cosmogo.utils.testing import admin_url

DEFAULT_LINK_TEMPLATE = '<a href="{url}">{label}</a>'


def admin_link(obj: Model, view='change', site=None, label=None, template=DEFAULT_LINK_TEMPLATE):
    url = admin_url(type(obj), view, obj.pk, site=site)
    link = template.format(url=url, obj=obj, label=label or obj)

    return mark_safe(link)


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

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class ReadOnlyModelAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    """
    Immutable admin for a given model.
    """
