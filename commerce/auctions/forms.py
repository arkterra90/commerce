from django.forms import ModelForm
from .models import *


class ListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = "__all__"
        exclude = ["list_user", "bid_current", "list_active"]
        labels = {
            'title': 'Title'
        }



class bidsForm(ModelForm):
    class Meta:
        model = bids
        fields = ["bid"]


class CommentsForm(ModelForm):
    class Meta:
        model = comments
        fields = ["item_comment"]
        exclude = ["item", "user_comment", "time_comment"]

class WatchForm(ModelForm):
    class Meta:
        model = Watch_List
        fields = ["watching"]