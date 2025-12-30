from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from django.views import View
from core.views import add_group_name_to_context
from .cart import Cart
from guardar.models import Producto
from django.http import JsonResponse
from django.contrib import messages

@add_group_name_to_context
class CartSummaryView(TemplateView):
    template_name = "cart/cart_summary.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Inicializar el carrito y obtener los productos
        cart = Cart(self.request)
        context['cart_products'] = cart.get_prods()
        context['quantities'] = cart.get_quants()
        context["totals"] = cart.cart_total()
        return context

def cart_add(request):
    cart = Cart(request)
    if request.POST.get("action") == "post":
        product_id = int(request.POST.get("product_id"))
        product_qty = int(request.POST.get("product_qty"))
        product = get_object_or_404(Producto, id_producto=product_id)  
        
        # Guardar en una sesión
        cart.add(product=product, quantity=product_qty)
        
        # Obtener la cantidad total de productos en el carrito
        cart_quantity = cart.__len__()
        
        # Retornar respuesta
        
        response = JsonResponse({'qty': cart_quantity})
        messages.success(request, "Producto agregado al carrito.")
        return response

def cart_delete(request):
    cart = Cart(request)
    if request.POST.get("action") == "post":
        product_id = request.POST.get("product_id")
        
        print("Received Product ID to delete:", product_id)
        
        if product_id:
            try:
                product_id = int(product_id)
                cart.delete(product=product_id)
                response = JsonResponse({"product": product_id})
            except ValueError:
                response = JsonResponse({"error": "Invalid input"}, status=400)
        else:
            response = JsonResponse({"error": "Missing input"}, status=400)
        messages.success(request, "Productos eliminado del carrito.")
        return response

def cart_update(request):
    cart = Cart(request)
    if request.POST.get("action") == "post":
            product_id = int(request.POST.get("product_id"))
            product_qty = int(request.POST.get('product_qty'))
            
            cart.update(product = product_id, quantity = product_qty)
            response = JsonResponse({"qty":product_qty})
            messages.success(request, "Productos actualizado.")
            return response
            #return redirect("cart_summary")
