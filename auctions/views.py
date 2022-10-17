from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from auctions import forms
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

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
    # Return the user to a page to add a new listing

    if request.method == "POST":
        form = forms.NewListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.user = request.user
            listing.save()
            return HttpResponseRedirect(reverse("auctions:index"))
        
    else:
        return render(request, "auctions/new_listing.html", {
            "new_listing_form" : forms.NewListingForm()
        })



def listing(request, id):

    # Display listing and its details

    # Take the title and search for a listing with that title
    # if that listing exsists, render it. 


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
                # "title": listing.title,

            })
        
    else:
        # I want to get the bid that the user submitted, and confirm it's acceptable. if so, add bid to db and update listing. else, return error
        # bid_form = forms.NewBidForm(request.POST or None)

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
        except Bid.DoesNotExist or None:

            #compare only to the listing price. no bids
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

    # Take the listing currently displayed on the page, and add it to the users watchlist


    listing = Listing.objects.get(id=id)
    
    try:
        listing_in_watchlist = WatchList.objects.get(listings= listing,user=request.user)
    except WatchList.DoesNotExist:
        listing_in_watchlist = None


    # if listing is in user watchlist
    if listing_in_watchlist != None:
            
        # IF THE CURRENT LISTING IS NOT IN USERS WATCHLIST
        # listing = WatchList.objects.get(user=request.user,listings=listing)
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
    # if listing not in user watchlist
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

    try:
        user_watchlist = WatchList.objects.get(user=request.user)
        return render(request, "auctions/watchlist.html", {
            "watchlist" : user_watchlist,
        })   
    
    except WatchList.DoesNotExist:
        user_watchlist = WatchList(user=request.user)
        user_watchlist.save()
        return render(request, "auctions/watchlist.html", {
            "watchlist" : user_watchlist,
        })   



@login_required
def close_listing(request, id):
    # when user clicks on close, then calculate the highest bid, and set the status to closed instead of active
    listing = Listing.objects.get(id=id)
    listing.active=False
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
    # if the user is authenticated
    # get the form input
    # validate data
    # if its clean, store the data in the comments database
    if request.method == "POST" and request.user.is_authenticated:
        listing = Listing.objects.get(id=id)
        comment_form = forms.NewCommentForm(request.POST)
        comment_form.save(commit=False)

        if comment_form.is_valid():
            # try:
            new_comment = Comment.objects.create(listings=listing, user=request.user)
            # except Comment.DoesNotExist:

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


def categories(request):
    # i want to display a list of the categories
    categories = sorted(Listing.CATEGORY_CHOICES)
    # categories = Listing(user=request.user,title="Dummy",details="FooBar",active=False)
    # I think i need to create an instance, or empty instance first, then return that and display it's choices
    return render(request, "auctions/categories.html", {
        "categories":categories,
    })


def category_listings(request, category):
    # I want to get a list of all listings with the category given

    listings = Listing.objects.filter(category=category)
    return render(request, "auctions/category_listings.html", {
        "listings":listings,
    })