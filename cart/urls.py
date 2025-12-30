from django.urls import path
from django.contrib.auth.decorators import login_required #valida que el usuario este logueado
from .views import CartSummaryView, cart_add, cart_update, cart_delete
from django.contrib.auth.decorators import login_required
urlpatterns = [
    path("", CartSummaryView.as_view(), name = "cart_summary"),
    path("add/",cart_add, name = "cart_add"),
    path("delete/",cart_delete, name = "cart_delete"),
    path("update/",cart_update, name = "cart_update"),
    

]