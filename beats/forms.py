from django.forms import ModelForm
from models import Beat

class BeatForm(ModelForm):
    class Meta:
        model = Beat
