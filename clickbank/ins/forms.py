from django import forms
from clickbank.ins.models import ClickBankINS

ClickBankINSForm(forms.ModelForm):
    """Form used to receive and record ClickBank INS."""

    class Meta:
        model = ClickBankINS
