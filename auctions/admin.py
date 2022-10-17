from django.contrib import admin

from auctions.models import Bid, Comment, Listing, WatchList

# Register your models here.
admin.site.register(Listing)
admin.site.register(Bid)
admin.site.register(Comment)
admin.site.register(WatchList)
