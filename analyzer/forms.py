from django import forms


class DatasetUploadForm(forms.Form):
    DOMAIN_CHOICES = [
        ('medical', 'Medical'),
        ('engineering', 'Engineering'),
    ]

    domain = forms.ChoiceField(
        choices=DOMAIN_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    file = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )