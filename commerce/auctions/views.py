from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

from .models import *
from .forms import *
from .categories import categories

# Loads index page and sends all data from listing model to 
# show user only active listings.
def index(request):
    return render(request, "auctions/index.html", {
        "listing": Listing.objects.filter(list_active=True),
        "categories": categories
    })

# category_view allows a user to view the categories.html page.
# Once a user selects a category to view on the categories page
# category_view returns all the listings in the selected category
# and renders them for the user. Categories are imported from .categories.
def category_view(request):
    if request.method == "POST":
        cat_name = request.POST['category']
        cat_view = Listing.objects.filter(category=cat_name)
        print(cat_view)
        return render(request, "auctions/categories.html", {
            "categories": categories,
            "cat_view": cat_view
        })
    else:
        return render(request, "auctions/categories.html", {
            "categories": categories
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
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

# Registers a new user.
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
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

# list_add renders a form based on django modelforms from the Listing model
# and allows a user to create a new user. The listing then creates a new item in
# listing model and the user has the option to create another listing and save the 
# one listing created. Based on user decision the user is taken back to index
# or the page is reloaded for the user to create another listing.
@login_required(redirect_field_name='index')    
def list_add(request):
    if request.method == "POST":
        if 'save' in request.POST:
            f = ListingForm(request.POST)
            if f.is_valid():
                instance = f.save(commit=False)
                instance.list_user = request.POST.get('list_user')
                instance.bid_current = instance.bid_start
                instance.list_active = True
                instance.save()
                return render(request, "auctions/index.html", {
                    "listing": Listing.objects.filter(list_active=True)
                     })
            else:
                return render(request, "auctions/list_add.html", {
                    "message": "Listing was not saved",
                    "ListingForm": ListingForm
                })
        if 'add' in request.POST:
            f = ListingForm(request.POST)
            if f.is_valid():
                instance = f.save(commit=False)
                instance.list_user = request.POST.get('list_user')
                instance.bid_current = instance.bid_start
                instance.save()
                return render(request, "auctions/list_add.html", {
                    "ListingForm": ListingForm
                })
            else:
                return render(request, "auctions/list_add.html", {
                    "message": "Listing was not saved",
                    "ListingForm": ListingForm
                })
    else:
        return render(request, "auctions/list_add.html", {
            "ListingForm": ListingForm
        })
    
# list_view allows a user to view all the details of a listing, place bids,
# leave comments, and add the item to their watch list. If the listing was 
# created by the user list_view also allows them to close the auction at which
# point the templete renders input fields blank and closes the auction announcing
# the winner.
@login_required(redirect_field_name='index')    
def list_view(request, list_id):
    list_item = Listing.objects.get(pk=list_id)
    
    # For a brand new item there will not be comments or bids so a
    # try/except is needed to handle for errors with the query 
    # where nothing would be returned.
    try:
        list_bid = bids.objects.filter(item=list_item)
    except (NameError, ObjectDoesNotExist):
        list_bid = None
    
    try:
        list_comment = comments.objects.filter(item=list_item)
    except (NameError, ObjectDoesNotExist):
        list_comment = None

    # Gets error message if a bid lower than current highest is placed
    bid_message = request.GET.get('bid_message', None)
    watch_message = request.GET.get('watch_message', None)

    # Populates action item info box with current highest bid.
    # If current highest bid is the starting bid then starting bid
    # is highest bid.
    high_bid = bids.objects.filter(item=list_item).order_by('-bid').first()
    high_bidder = high_bid.bid_user
    if high_bid == None:
        high_bid = list_item.bid_start
    elif high_bid != None:
        high_bid = high_bid.bid
        print(high_bid)


    return render(request, "auctions/list_view.html",{
        "list_item": list_item,
        "BidForm": bidsForm,
        "CommentsForm": CommentsForm, 
        "list_bid": list_bid,
        "list_comment": list_comment,
        "bid_message": bid_message,
        "watch_message": watch_message,
        "high_bid": high_bid,
        "high_bidder": high_bidder,
        "WatchForm": WatchForm
    })

# item_comments takes user input for comments from list_view template, 
# stores comments to comment's model and then HttpResponseRedirect's the user
# back to list_view for an updated list_view containing their comment.
def item_comments(request, list_id):
    listing = Listing.objects.get(pk=list_id)
    f = CommentsForm(request.POST)
    if f.is_valid:
        instance = f.save(commit=False)
        instance.user_comment = request.POST.get('bid_user')
        instance.item = listing
        instance.save()
        return HttpResponseRedirect(reverse("list_view", args=(listing.id,)))
    
# bid_place is a function of the list_view page. 
# Allows any logged in user to place a bid. Checks to make sure
# bid being placed is both higher than the starting bid and the
# current highest bid. If both true, bid is saved in models and
# user is reloaded to the auction page.    
def bid_place(request, list_id):
    listing = Listing.objects.get(pk=list_id)
    f = bidsForm(request.POST)
    if f.is_valid:
        instance = f.save(commit=False)
        #instance.bid must be greater than previous bid
        item_bids = bids.objects.filter(item=listing)
        highest_bid = item_bids.order_by('-bid').first()
        if highest_bid == None:
            if instance.bid > listing.bid_start:
                instance.bid_user = request.POST.get('bid_user')
                instance.item = listing
                listing.bid_current = instance.bid
                listing.save()
                instance.save()
                return HttpResponseRedirect(reverse("list_view", args=(listing.id,)))
            else:
                return HttpResponseRedirect(reverse("list_view", args=(listing.id,)) + f"?bid_message=Place%20a%20bid%20higher%20than%20current%20bid.")
        elif highest_bid.bid > instance.bid:
            return HttpResponseRedirect(reverse("list_view", args=(listing.id,)) + f"?bid_message=Place%20a%20bid%20higher%20than%20current%20bid.")
        else:
            instance.bid_user = request.POST.get('bid_user')
            instance.item = listing
            listing.bid_current = instance.bid
            listing.save()
            instance.save()
            return HttpResponseRedirect(reverse("list_view", args=(listing.id,)))
        
# watch_list is a fucntion of the list_view page.
# Saves a listing to Watch_List model. Checks if user is currently watching
# the item and does not repeat saves and sends error message notifying user they
# are already watching the item. Send user back to the auctions page with
# appropriate updates made to page.
def watch_list (request, list_id):
    listing= Listing.objects.get(pk=list_id)
    
    user = request.POST.get('user')
    try:
        watch = Watch_List.objects.get(item=listing, watch_user=user)
    except (NameError, ObjectDoesNotExist):
        watch = None
    if watch != None and watch.watching == True:
        watch.watching = False
        watch.save()
        return HttpResponseRedirect(reverse("list_view", args=(listing.id,)) + f"?watch_message=Listing%20removed%20from%20watch%20list.")
    elif watch != None and watch.watching == False:
        watch.watching = True
        watch.save()
        return HttpResponseRedirect(reverse("list_view", args=(listing.id,)) + f"?watch_message=Listing%20saved%20to%20watch%20list.")
    else:
        f = WatchForm(request.POST)
        if f.is_valid:
            instance = f.save(commit=False)
            instance.watch_user = user
            instance.item = listing
            instance.save()
            return HttpResponseRedirect(reverse("list_view", args=(listing.id,)) + f"?watch_message=Listing%20saved%20to%20watch%20list.")
        else:
            return HttpResponseRedirect(reverse("list_view", args=(listing.id,)) + f"?watch_message=Listing%20not%20saved%20to%20watch%20list.")

# bid_close is a function of the list_view page.
# Allows the creator of an auction to close bidding.
def bid_close (request, list_id):
    listing = Listing.objects.get(pk=list_id)
    close = request.POST.get('user_bid_close')
    listing.list_active = close
    listing.save()
    return HttpResponseRedirect(reverse("list_view", args=(listing.id,)))

# watch_list renders the watch list of a user using the watch.html template. This
# template takes no input and only renders listing the user has selected to be on 
# their watch list.
def watch(request, user_name):
    watch_list = Watch_List.objects.filter(watch_user=user_name, watching=True)
    return render(request, "auctions/watch.html", {
        "user_name": user_name,
        "watch_list": watch_list
    })