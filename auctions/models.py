from tkinter import CASCADE
from typing_extensions import Required
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import requests



# TODO
# ADD USERS TO RELEVANT MODELS


class User(AbstractUser):
    pass


# class Bid(models.Model):
#     bids = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
#     # starting_bid = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="starting_bid")
#     time_submitted = models.DateTimeField(blank=False, default=timezone.now)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     def __str__(self):
#         return f"{self.bids}"
    


class Listing(models.Model):
    # listing_image = models.ImageField(upload_to='uploads')
    # id = models.AutoField
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    details = models.TextField(max_length=300)
    # price = models.ForeignKey(Bid, on_delete=models.CASCADE, blank=True, related_name="bid_price")
    CATEGORY_CHOICES = [
        ("FOOD", "FOOD"),
        ("ELECTRONICS", "ELECTRONICS"),
        ("CLOTHING", "CLOTHING"),
        ("ACCESSORIES", "ACCESSORIES"),
        ("CONTENT", "CONTENT"),
        ("SERVICE", "SERVICE"),
        ("MUSIC", "MUSIC"),
        ("ENTERTAINMENT", "ENTERTAINMENT"),
        ("HOME EQUIPMENT", "HOME EQUIPMENT"),
        ("ART","ART"),
        ("AUTO INDUSTRY", "AUTO INDUSTRY"),
        ("PETS", "PETS"),
        ("MISC ITEMS", "MISC ITEMS"),
        ("NONE","NONE"),
    ]
    category = models.CharField(
        max_length=15,
        choices=CATEGORY_CHOICES,
        default="NONE",
    )
    created = models.DateTimeField

    image_url = models.ImageField(null=True, blank=True, upload_to='images/')
    # image_url_2 = models.ImageField(blank=True)
    active = models.BooleanField(default=True)
    time_submitted = models.DateTimeField(blank=False, default=timezone.now)
    winner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="winner")

    # def __init__(self):
    #     return f"{self.title}"
    def __str__(self):
        return f"{self.title}"


class Bid(models.Model):
    bid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    time_submitted = models.DateTimeField(blank=False, default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.bid}"


class WatchList(models.Model):
    listings = models.ManyToManyField(Listing, related_name="watched")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # watched = models.BooleanField(default=False, blank=False)

    def __str__(self):
        return f"{self.user}"


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listings = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listing_comments")
    comment = models.CharField(max_length=150, blank=False)
    time_submitted = models.DateTimeField(blank=False, default=timezone.now)
    
    def __str__(self):
        return f"{self.comment}"
