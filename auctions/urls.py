from django.urls import path

from . import views


app_name = "auctions"
urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new_listing", views.new_listing, name="new_listing"),
    path("<int:id>/", views.listing, name="id"),
    path("watchlist/", views.watchlist_view, name="watchlist_view"),
    path("watchlist/<int:id>/", views.watchlist, name="watchlist"),
    path("close_listing/<int:id>/", views.close_listing, name="close_listing"),
    path("new_comment/<int:id>/", views.new_comment, name="new_comment"),
    path("categories/", views.categories, name="categories"),
    path("category_listings/<str:category>/", views.category_listings, name="category_listings"),
]
