from . import models
from django import forms

class NewListingForm(forms.ModelForm):
    class Meta:
        model = models.Listing
        fields = ['title', 'details', 'category','price', 'image_url']
        # widgets = {
        #     'fields': forms.TextInput(attrs={'class': 'form-column'}),
        # }


class NewBidForm(forms.ModelForm):
    class Meta:
        model = models.Bid
        fields = ['bid']


class NewCommentForm(forms.ModelForm):
    class Meta:
        model = models.Comment
        fields = ['comment']