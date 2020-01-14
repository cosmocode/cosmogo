from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.http import Http404

from cosmogo.utils.gettext import trans


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
