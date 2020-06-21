from django import forms
from .utils import get_songs_in_songbook


class SongsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(SongsForm, self).__init__(*args, **kwargs)
        for k, v in get_songs_in_songbook().items():
            self.fields["~_" + v] = forms.BooleanField(label=k, initial=False, required=False)

    def checkboxes(self):
        for name, value in self.cleaned_data.items():
            if name.startswith("~_"):
                yield (name.replace("~_", ""), value)
                # yield (self.fields[name].label, name.split["~_"], value)
