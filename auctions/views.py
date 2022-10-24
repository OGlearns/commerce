from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from auctions import forms
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser

from .models import *


def index(request):
    # listings = 
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.filter(active=True),
        "bids" : Bid.objects.all(),
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("auctions:index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("auctions:index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("auctions:index"))
    else:
        return render(request, "auctions/register.html")


def new_listing(request):
    # save new listing if it is valid
    if request.method == "POST":
        form = forms.NewListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.user = request.user            
            listing.save()
            return HttpResponseRedirect(reverse("auctions:index"))
        
    # Return the user to a page to add a new listing
    else:
        return render(request, "auctions/new_listing.html", {
            "new_listing_form" : forms.NewListingForm()
        })



def listing(request, id):
    # get requested listing, return listing
    if request.method == "GET":
        if request.user.is_authenticated:
            try:
                listing = Listing.objects.get(id=id)
                try:
                    watchlist = WatchList.objects.get(user=request.user)
                except WatchList.DoesNotExist:
                    watchlist = WatchList(user=request.user)
                return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "title": listing.title,
                    "watchlist" : watchlist,
                    "NewBidForm" : forms.NewBidForm(),
                    "NewCommentForm": forms.NewCommentForm(),
                    "comments":Comment.objects.filter(listings=listing)
                })
            except Listing.DoesNotExist or TypeError or NameError or None:
                return render(request, "auctions/listing.html", {
                    "listing": None,
                    "title": listing.title,
                    "error": 'Error. No listing found.',
                    "watchlist" : WatchList.objects.get(user=request.user),
                    "NewBidForm" : forms.NewBidForm(),
                    "NewCommentForm": forms.NewCommentForm(),
                    "comments":Comment.objects.filter(listings=listing)
                })
        else:
            listing = Listing.objects.get(id=id)
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "comments":Comment.objects.filter(listings=listing),
            })
    # handle new bid attempt on listing page
    else:
        bid_form = forms.NewBidForm(request.POST)
        bid_form.save(commit=False)


        listing = Listing.objects.get(id=id)
        try:
            WatchList.objects.get(user=request.user)

            if bid_form.is_valid():
                listing_bid = Bid.objects.get(listing=listing)

                if  bid_form.cleaned_data['bid'] < listing.price:
                    return render(request, "auctions/listing.html", {
                        "error" : "The bid submitted is equal to or less than the starting price.",
                        "listing": listing,
                        "watchlist" : WatchList.objects.get(user=request.user),
                        "NewBidForm" : forms.NewBidForm(),
                        "NewCommentForm": forms.NewCommentForm(),
                        "comments":Comment.objects.filter(listings=listing)
                    })
                if bid_form.cleaned_data['bid'] <= listing_bid.bid:

                    return render(request, "auctions/listing.html", {
                        "error" : "You uh... you sure you don't want to bid higher? You should bid higher.",
                        "listing": listing,
                        "watchlist" : WatchList.objects.get(user=request.user),
                        "NewBidForm" : forms.NewBidForm(),
                        "NewCommentForm": forms.NewCommentForm(),
                        "comments":Comment.objects.filter(listings=listing)
                    })
                listing_bid.bid = bid_form.cleaned_data['bid']
                listing_bid.save()
                return render (request, "auctions/listing.html", {
                        "listing": listing,
                        "watchlist" : WatchList.objects.get(user=request.user),
                        "NewBidForm" : forms.NewBidForm(),
                        "NewCommentForm": forms.NewCommentForm(),
                        "comments":Comment.objects.filter(listings=listing)
                })
        except Bid.DoesNotExist or None: # FIX TO WATCHLIST.DOESNOTEXIST?

            new_bid = bid_form.cleaned_data['bid']
            if  listing.price > new_bid:
                bid_form.save(commit=False)
                return render(request, "auctions/listing.html", {
                    "error" : "The bid submitted is equal to or less than the listing price.",
                    "listing": listing,
                    "watchlist" : WatchList.objects.get(user=request.user),
                    "NewBidForm" : forms.NewBidForm(),
                    "NewCommentForm": forms.NewCommentForm(),
                    "comments":Comment.objects.filter(listings=listing)
                })
            else:
                listing_bid = Bid.objects.create(user = request.user, listing=listing)
                listing_bid.bid = bid_form.cleaned_data['bid']
                listing_bid.save()
                return render (request, "auctions/listing.html", {
                        "listing": listing,
                        "watchlist" : WatchList.objects.get(user=request.user),
                        "NewBidForm" : forms.NewBidForm(),
                        "NewCommentForm": forms.NewCommentForm(),
                        "comments":Comment.objects.filter(listings=listing)
                })

@login_required
def watchlist(request, id):

    listing = Listing.objects.get(id=id)
    # try to get users watchlist
    try:
        listing_in_watchlist = WatchList.objects.get(listings= listing,user=request.user)
    except WatchList.DoesNotExist:
        listing_in_watchlist = None
    #remove listing from watchlist if listing is in users watchlist
    if listing_in_watchlist != None:
        listing_in_watchlist.listings.remove(listing)
        listing_in_watchlist.save()


        return render(request, "auctions/listing.html", {
            "listing": listing,
            "watchlist" : WatchList.objects.get(user=request.user),
            "NewBidForm" : forms.NewBidForm(),
            "NewCommentForm": forms.NewCommentForm(),
            "comments":Comment.objects.filter(listings=listing)
        })   
    else:
    # if listing not in user watchlist, add listing to watchlist
        try:
            watched_listings = WatchList.objects.get(user=request.user)
        except WatchList.DoesNotExist:
            watched_listings = WatchList.objects.create(user=request.user)

        watched_listings.listings.add(listing)
        watched_listings.save()
        return render(request, "auctions/listing.html", {
            "listings": watched_listings,
            "listing": listing,
            "title": listing.title,
            "watchlist" :  WatchList.objects.get(user=request.user),
            "NewBidForm" : forms.NewBidForm(),
            "NewCommentForm": forms.NewCommentForm(),
            "comments":Comment.objects.filter(listings=listing)
        })


@login_required
def watchlist_view(request):
    # try to go to users watchlist
    try:
        user_watchlist = WatchList.objects.get(user=request.user)
        return render(request, "auctions/watchlist.html", {
            "watchlist" : user_watchlist,
        })   
    # if user has no watchlist, create one and go to it
    except WatchList.DoesNotExist:  
        user_watchlist = WatchList(user=request.user)
        user_watchlist.save()
        return render(request, "auctions/watchlist.html", {
            "watchlist" : user_watchlist,
        })   



@login_required
def close_listing(request, id):

    # get requested listing
    listing = Listing.objects.get(id=id)
    # close the listing
    listing.active=False

    # check who the winner is, return it
    try:
        listing_bid = Bid.objects.get(listing=listing)
    except Bid.DoesNotExist:
        listing_bid = None

    if listing_bid:
        listing.winner = listing_bid.user

    else:
        listing.winner = listing.user
    listing.save()
    
    return render(request, "auctions/listing.html", {
        "listing":listing,
        "watchlist" :  WatchList.objects.get(user=request.user),
        "NewBidForm" : forms.NewBidForm(),
        "winner":listing.winner,
        "NewCommentForm": forms.NewCommentForm(),
        "comments":Comment.objects.filter(listings=listing)
    })

@login_required
def new_comment(request, id):
    # get and save new comment if it is valid
    if request.method == "POST":

        listing = Listing.objects.get(id=id)

        comment_form = forms.NewCommentForm(request.POST)
        comment_form.save(commit=False)


        if comment_form.is_valid():

            new_comment = Comment.objects.create(listings=listing, user=request.user)

            new_comment.comment = comment_form.cleaned_data["comment"]
            new_comment.save()
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "watchlist" :  WatchList.objects.get(user=request.user),
                "NewBidForm" : forms.NewBidForm(),
                "NewCommentForm": forms.NewCommentForm(),
                "comments":Comment.objects.filter(listings=listing)
            })
        pass


    # get and return a list of the categories
def categories(request):
    categories = sorted(Listing.CATEGORY_CHOICES)
    return render(request, "auctions/categories.html", {
        "categories":categories,
    })

    # get and return list of listings in each category
def category_listings(request, category):
    listings = Listing.objects.filter(category=category)
    return render(request, "auctions/category_listings.html", {
        "listings":listings,
    })