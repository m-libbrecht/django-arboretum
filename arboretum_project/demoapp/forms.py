from django import forms

from arboretum.widgets import  FancyTreeWidget
from demoapp.models import Domain

domains = Domain.objects.all()


# class TreeForm(forms.Form):
#     domains = forms.ModelMultipleChoiceField(
#         queryset = domains,
#         widget = FancyTreeWidget(queryset=domains,select_mode=2, checkbox=True,  containermode = False)
#     )


class TreeForm(forms.Form):
    domains = forms.ModelMultipleChoiceField(
        queryset = domains,
        widget = FancyTreeWidget(queryset=domains),

    )