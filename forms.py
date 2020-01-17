from django import forms


class AutoCompleteMixin:
    autocomplete = {}

    def __init__(self, *args, **kwargs):
        assert isinstance(self, forms.BaseForm)

        super(AutoCompleteMixin, self).__init__(*args, **kwargs)

        for field in set(self.fields) & set(self.autocomplete):
            self.fields[field].widget.attrs['autocomplete'] = self.autocomplete[field]
