from django.contrib.auth.models import AbstractUser
from django.db import models
from .categories import categories



class User(AbstractUser):
    pass

# Listing model contains all details of a listing.
class Listing(models.Model):
    

    title = models.CharField(verbose_name='Listing Title', max_length=64)
    discription = models.TextField(verbose_name='Listing Discription')
    # Categories are imported from categories.py 
    category = models.CharField(max_length=9, choices=categories, default="")
    bid_start = models.DecimalField(verbose_name='Starting Bid', max_digits=10, decimal_places=2, default='0.00')
    bid_current = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    list_user = models.CharField(verbose_name='Listing User', max_length=64, null=True, blank=True)
    list_time = models.DateTimeField(auto_now_add=True)
    image_url = models.URLField(null=True, blank=True)
    list_active = models.BooleanField()
    def __str__(self):
        return f"{self.id}: {self.title} {self.discription} {self.category} {self.list_user} {self.image_url}"

# bids model keeps track of bids and is foreignkeyed to Listing.
class bids(models.Model):
    item = models.ForeignKey(Listing, on_delete=models.CASCADE)
    bid = models.DecimalField(max_digits=10, decimal_places=2)
    bid_time = models.DateTimeField(auto_now_add=True)
    bid_user = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.id}: {self.item} {self.bid} {self.bid_time} {self.bid_user}"
    
# comments model keeps track of comments and is foreignkeyed to Listing.
class comments(models.Model):
    item = models.ForeignKey(Listing, on_delete=models.CASCADE)
    item_comment = models.TextField(verbose_name='Comment')
    user_comment = models.CharField(max_length=64)
    time_comment = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id}: {self.item} {self.item_comment} {self.user_comment} {self.time_comment}"
    
# Watch_List model keeps track of listing a user would like to keep on their watch list.
class Watch_List(models.Model):
    item = models.ForeignKey(Listing, on_delete=models.CASCADE)
    watch_user = models.CharField(max_length=64)
    watching = models.BooleanField(verbose_name='Watch List', default=False)

    def __str__(self):
        return f"{self.id}: {self.item} {self.watch_user} {self.watching}"