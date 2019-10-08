from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.http import Http404

from cosmogo.utils.gettext import trans


class DefaultTabularInline(admin.TabularInline):
    template = 'admin/inline/tabular-without-original.html'
    extra = 0


class AdminViewMixin:

    def get_object_for_change(self: admin.ModelAdmin, request, object_id):
        obj = self.get_object(request, object_id)

        if not self.has_change_permission(request, obj=obj):
            raise PermissionDenied

        if obj is None:
            msg = trans('%(name)s object with primary key %(key)r does not exist.')
            context = {'name': self.opts.verbose_name, 'key': object_id}

            raise Http404(msg % context)

        return obj
