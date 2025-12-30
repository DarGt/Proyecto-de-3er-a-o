from core.views import add_group_name_to_context
from cart.cart import Cart
from django.views.generic import TemplateView
from payment.forms import ShippingForm, PaymentForm
from payment.models import ShippingAddress, Order, OrderItem
from django.contrib import messages
from django.shortcuts import redirect,render,get_object_or_404
from django.contrib.auth.mixins import UserPassesTestMixin , LoginRequiredMixin
from django.contrib.auth.models import User
from django.views import View
from django.utils.timezone import now
from django.views.generic import CreateView
from accounts.models import Usuario
from django.urls import reverse
from decimal import Decimal
import stripe
from django.conf import settings
from datetime import datetime
from guardar.models import Producto
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from weasyprint import HTML
from django.http import HttpResponse
import os
from django.templatetags.static import static
stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = settings.STRIPE_API_VERSION

#funcion para ver las ordenes
@add_group_name_to_context
class OrderDetailView(UserPassesTestMixin, LoginRequiredMixin, TemplateView):
    template_name = "payment/orders.html"

    def test_func(self):
        # Verifica si el usuario es superusuario
        return self.request.user.is_authenticated and self.request.user.is_superuser

    def handle_no_permission(self):
        # Redirige a la página de error con un mensaje
        messages.error(self.request, "Access Denied")
        return redirect("error")

    def get_context_data(self, **kwargs):
        # Obtiene el contexto base
        context = super().get_context_data(**kwargs)
        # Obtiene la orden y los elementos de la orden
        pk = self.kwargs.get('pk')  # Obtiene el ID de la orden desde la URL
        context["order"] = Order.objects.get(id=pk)
        context["items"] = OrderItem.objects.filter(order=pk)
        n= OrderItem.objects.filter(order=pk)
        
        return context

    def post(self, request, *args, **kwargs):
        # Obtiene el estado de envío desde el formulario
        status = request.POST.get('shipping_status')
        pk = self.kwargs.get('pk')  # Obtiene el ID de la orden desde la URL
        # Obtiene la orden
        order = Order.objects.filter(id=pk)
        # Actualiza el estado de la orden
        if status == "true":
            current_time = now()
            order.update(shipped=True, date_shipped=current_time)
            messages.success(request, "Envio actualizados")
            return redirect('shipped_dash')
        else:
            order.update(shipped=False)
            # Redirige con un mensaje de éxito
            messages.success(request, "Envio actualizados")
            return redirect('not_shipped_dash')
        

#funcion para pedidos no enviados
@add_group_name_to_context
class NotShippedDashView(UserPassesTestMixin, LoginRequiredMixin, TemplateView):
    template_name = "payment/not_shipped_dash.html"

    def test_func(self):
        # Verifica si el usuario es superusuario o staff
        return self.request.user.is_superuser or self.request.user.is_staff

    def handle_no_permission(self):
        # Redirige a la página de error con un mensaje
        messages.error(self.request, "Access Denied")
        return redirect("error")

    def get_context_data(self, **kwargs):
        # Obtiene el contexto base
        context = super().get_context_data(**kwargs)
        # Agrega las órdenes no enviadas al contexto
        context["orders"] = Order.objects.filter(shipped=False)
        return context

    def post(self, request, *args, **kwargs):
        # Obtiene el estado de envío y el ID de la orden desde el formulario
        status = request.POST.get('shipping_status')
        num = request.POST.get('num')
        # Obtiene la orden
        order = Order.objects.filter(id=num)
        # Obtiene la fecha y hora actual
        current_time = now()
        # Actualiza la orden
        order.update(shipped=True, date_shipped=current_time)
        # Redirige con un mensaje de éxito
        messages.success(request, "Envio actualizados")
        return redirect('shipped_dash')

#funcion para pedidos enviados
@add_group_name_to_context
class ShippedDashView(UserPassesTestMixin, LoginRequiredMixin, TemplateView):
    template_name = "payment/shipped_dash.html"

    def test_func(self):
        # Verifica si el usuario es superusuario o staff
        return self.request.user.is_superuser or self.request.user.is_staff

    def handle_no_permission(self):
        # Redirige a la página de error con un mensaje
        messages.error(self.request, "Access Denied")
        return redirect("error")

    def get_context_data(self, **kwargs):
        # Obtiene el contexto base
        context = super().get_context_data(**kwargs)
        # Agrega las órdenes enviadas al contexto
        context["orders"] = Order.objects.filter(shipped=True)
        return context

    def post(self, request, *args, **kwargs):
        # Obtiene el estado de envío y el ID de la orden desde el formulario
        status = request.POST.get('shipping_status')
        num = request.POST.get('num')
        # Obtiene la orden
        order = Order.objects.filter(id=num)
        # Obtiene la fecha y hora actual
        current_time = now()
        # Actualiza la orden
        order.update(shipped=False)
        # Redirige con un mensaje de éxito
        messages.success(request, "Envio actualizados")
        return redirect('not_shipped_dash')


#funcion para el cambio de datos de el formulario de envio 
def payment_succes(request):
    return render(request,"payment/paymet_succes.html",{}) 


#funcion para realizar pago
@add_group_name_to_context
class CheckoutView(UserPassesTestMixin, LoginRequiredMixin,TemplateView):
    template_name = "payment/checkout.html"
    
    def test_func(self):
        #return self.request.user.is_superuser or self.request.user.is_staff #si est trabajador o admin
        return self.request.user#!solo usuarios administrativos pueden acceder
        #redirijoa pagina de error
    def handle_no_permission(self):
        messages.success(self.request,"Debe iniciar sesión para continuar.")
        return redirect("login")#http://127.0.0.1:8000/agregar_usuario/

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Inicializar el carrito y obtener los productos
        cart = Cart(self.request)
        context['cart_products'] = cart.get_prods()
        context['quantities'] = cart.get_quants()
        context["totals"] = cart.cart_total()

        return context
    
    def post(self, request, *args, **kwargs):
        
     if request.user.is_authenticated:
        form_type = request.POST.get("form_type")
        if form_type == "shipping_form":  # Formulario de dirección de envío
            
            user = self.request.user
            # Obtén la dirección de envío existente o crea una nueva
            shipping_address, created = ShippingAddress.objects.get_or_create(user=user) 
            shipping_form = ShippingForm(request.POST, instance=shipping_address)

            if shipping_form.is_valid():
                
                shipping_form.save()
                messages.success(request, "Información de envío actualizada correctamente.")
                return redirect("checkout")
            else:
               messages.error(request,"Hubo un error al actualizar la información de envío.")

            context = self.get_context_data()
            context["shipping_form"] = shipping_form
            return render(request, "payment/checkout.html", context)
        
     else:
         #aqui paso tambien el formulario si no esta logueado o no es usuario
         messages.success(request, "Debe iniciar sesión para continuar.")
         return redirect("login")  # Redirige al inicio de sesión con la URL de retorno


#funcion que permite realizar pagos
@add_group_name_to_context
class BillingInfoView(TemplateView):
    template_name = "payment/billing_info.html"

    def post(self, request, *args, **kwargs):
        cart = Cart(request)
        cart_products = cart.get_prods()
        quantities = cart.get_quants()
        totals = cart.cart_total()
        #creamos un secion co informacion de envio
        my_shipping = request.POST.dict()  # Convierte a un diccionario serializable
        request.session["my_shipping"] = my_shipping
        
        # Extraer solo los nombres de los productos
        product_names = [product.nombre for product in cart_products]

        shipping_form = request.POST

        context = {
            "cart_products": cart_products,
            "quantities": quantities,
            "totals": totals,
            "shipping_form": shipping_form,
        }
        print(product_names)
        
        #validamos si esta loguedado el usuario
                #validamos si esta loguedado el usuario
        if request.user.is_authenticated:
        # Extraer los datos del formulario y pasarlos al contexto
        # Inicializar el formulario de pago
            payment_form = PaymentForm()

            # Pasar los datos del formulario de envío al contexto
            context["payment_form"] = payment_form
            context["shipping_form_data"] = shipping_form.dict()
        else:
        # Si no está logueado, manejar el caso
            messages.success(request, "Debe iniciar sesión para continuar.")
            return redirect("login")
        
        # Combina el contexto adicional del decorador con el contexto local
        if hasattr(self, 'extra_context'):
            context.update(self.extra_context)
        
        return render(request, self.template_name, context)
    
@add_group_name_to_context
class PaymentProcessView(TemplateView):
    template_name = "payment/process.html"

    def post(self, request, *args, **kwargs):
        # Recuperar los datos de la orden desde la sesión
        order_data = request.session.get("order_data", None)
        if not order_data:
            messages.error(request, "No se encontraron datos de la orden.")
            return redirect("checkout")  # Redirige al checkout si no hay datos de la orden

        # Configurar URLs de éxito y cancelación
        success_url = request.build_absolute_uri(reverse("completed"))
        cancel_url = request.build_absolute_uri(reverse("canceled"))
        session_data = {
            "mode": "payment",
            "client_reference_id": order_data["user_id"],  # Puedes usar el ID del usuario como referencia
            "success_url": success_url,
            "cancel_url": cancel_url,
            "line_items": []
        }

        # Accede a los elementos del carrito desde los datos de la sesión
        for item in order_data["cart_products"]:
            session_data["line_items"].append({
                "price_data": {
                    "unit_amount": int(Decimal(item["price"]) * Decimal("100")),  # Convertir a centavos
                    "currency": "usd",
                    "product_data": {"name": f"Producto {item['product_id']}"},
                },
                "quantity": item["quantity"],
            })

        try:
            # Crear la sesión de Stripe
            session = stripe.checkout.Session.create(**session_data)
            return redirect(session.url, code=303)

        except stripe.error.StripeError as e:
            # Manejo de errores de Stripe
            messages.error(request, f"Error al procesar el pago: {e.user_message}")
            return redirect("canceled")

    def get(self, request, *args, **kwargs):
        # Renderiza la plantilla si se accede con GET
        return super().get(request, *args, **kwargs)
        
#funcion para el procesar ordenes y pagos
def process_order(request):
    # Verificar si el usuario está autenticado
    if not request.user.is_authenticated:
        messages.error(request, "Debe iniciar sesión para continuar.")
        return redirect("login")  # Redirige al inicio de sesión

    if request.POST:
        cart = Cart(request)
        cart_products = cart.get_prods()
        quantities = cart.get_quants()
        totals = cart.cart_total()

        my_shipping = request.session.get("my_shipping")

        # Generar los datos de la orden
        full_name = my_shipping['shipping_full_name']
        email = my_shipping['shipping_email']
        shipping_address = f"{my_shipping['shipping_address1']}\n{my_shipping['shipping_city']}\n{my_shipping['shipping_state']}\n{my_shipping['shipping_zipcode']}\n{my_shipping['shipping_country']}"
        amount_paid = str(totals)  # Convertir a string para evitar problemas de serialización

        # Almacenar los datos de la orden en la sesión
        request.session["order_data"] = {
            "user_id": request.user.id,
            "full_name": full_name,
            "email": email,
            "shipping_address": shipping_address,
            "amount_paid": amount_paid,  # Convertido a string
            "cart_products": [
                {
                    "product_id": product.id_producto,
                    "price": str(product.sale_price if product.is_sale else product.precio_venta),  # Convertido a string
                    "quantity": quantities[str(product.id_producto)],
                }
                for product in cart_products
            ],
        }

        # Redirigir al proceso de pago
        return redirect(reverse("process"))
    else:
        messages.error(request, "Debe enviar los datos del formulario.")
        return redirect("checkout")


@add_group_name_to_context
class PaymentCompletedView(TemplateView):
    template_name = "payment/completed.html"

    def get(self, request, *args, **kwargs):
        # Recuperar los datos de la orden desde la sesión
        order_data = request.session.get("order_data", None)
        if not order_data:
            messages.error(request, "No se encontraron datos de la orden.")
            return redirect("index")

        # Crear la orden en la base de datos
        user = User.objects.get(id=order_data["user_id"]) if order_data["user_id"] else None
        create_order = Order.objects.create(
            user=user,
            full_name=order_data["full_name"],
            email=order_data["email"],
            shipping_address=order_data["shipping_address"],
            amount_paid=Decimal(order_data["amount_paid"]),  # Convertir de string a Decimal
            method="Stripe",# Establecer el método de pago como "Stripe"
        )

        # Crear los elementos de la orden y actualizar el la existencia de los productos
        for item in order_data["cart_products"]:
            product = Producto.objects.get(id_producto=item["product_id"])  # Obtener el producto
            product.existencia -= item["quantity"]  # Restar la cantidad comprada
            product.save()  # Guardar los cambios en la base de datos
            
            OrderItem.objects.create(
                order=create_order,
                product_id=item["product_id"],
                user=user,
                quantity=item["quantity"],
                price=Decimal(item["price"]),  # Convertir de string a Decimal
            )

        
        
        # Limpiar los datos de la sesión
        del request.session["order_data"]

        # Borrar el carrito de la sesión
        for key in list(request.session.keys()):
            if key == "session_key":
                del request.session[key]
                
                
        # Borrar el carrito de la sesió

        # Borrar el carrito de la base de datos (campo old_cart)
        current_user = Usuario.objects.filter(user__id=request.user.id)
        current_user.update(old_cart="")
        
        
        #envio de correos s
        template = render_to_string('html_para_correos/coreo_de_orden_n.html', {
            'name': create_order.full_name,
            'email': create_order.email,
            'subject': 'Pedido Confirmado - ' + str(create_order.id),
            'message': 'Gracias por tu compra. Aquí están los detalles de tu pedido.',
            'order_id': create_order.id,
            'amount_paid': create_order.amount_paid,
            'shipping_address': create_order.shipping_address,
            
            'products': [
                {
            'name': Producto.objects.get(id_producto=item["product_id"]).nombre,
            'quantity': item["quantity"],
            'price': Decimal(item["price"])
                }
                for item in order_data["cart_products"]
            ]
        })
        staff_users = User.objects.filter(is_staff=True)
        admin_emails = [user.email for user in staff_users]  # Obtener los correos de los staff

        # Agregar correos adicionales si es necesario
        admin_emails.extend([ "basuradecorreo2002@gmail.com"])
        
        # Configurar el envío de correo
        emailSender = EmailMessage(
        subject='Confirmación de Pedido - #' + str(create_order.id),
        body=template,
        from_email=settings.EMAIL_HOST_USER,
        to=admin_emails
        )
        emailSender.content_subtype = 'html'
        emailSender.fail_silently = False
        emailSender.send()

        # Mensaje de éxito
        messages.success(request, "Pago realizado con éxito.")
        return super().get(request, *args, **kwargs)


@add_group_name_to_context
class PaymentCanceledView(TemplateView):
    template_name = "payment/canceled.html"

    def get(self, request, *args, **kwargs):
        # Mensaje de error
        messages.error(request, "El pago fue cancelado. No se realizaron cambios.")
        return super().get(request, *args, **kwargs)

from datetime import datetime
from django.contrib import messages

@add_group_name_to_context
class ComprasView(LoginRequiredMixin, TemplateView):
    template_name = "payment/compras.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user  # Usuario autenticado

        # Obtener todas las órdenes del usuario
        orders = Order.objects.filter(user=user)

        # Obtener los parámetros de búsqueda
        search_query = self.request.GET.get("search", "").strip()
        date_query = self.request.GET.get("date", "").strip()

        # Filtrar por número de orden si se proporciona
        if search_query.isdigit():
            orders = orders.filter(id=search_query)

        # Filtrar por fecha si se proporciona (sin necesidad de hora)
        if date_query:
            try:
                date_obj = datetime.strptime(date_query, "%Y-%m-%d")
                orders = orders.filter(date_ordered__date=date_obj.date())
            except ValueError:
                context["error"] = "Formato de fecha inválido. Use: '2025-05-05'."

        # Si no hay órdenes después del filtrado, mostrar mensaje de 'No encontrado'
        if not orders.exists():
            messages.warning(self.request, "No se encontraron órdenes con los criterios de búsqueda.")
            context["orders"] = []  # Pasar lista vacía
        else:
            context["orders"] = orders  # Pasar las órdenes filtradas

        return context
    def post(self, request, *args, **kwargs):
        # Obtener los datos del formulario
        shipping_status = request.POST.get("shipping_status")
        num = request.POST.get("num")
        user = request.user

        # Solo permitir que el usuario marque sus propias órdenes como recibidas
        try:
            order = Order.objects.get(id=num, user=user)
        except Order.DoesNotExist:
            messages.error(request, "Orden no encontrada o no autorizada.")
            return self.get(request, *args, **kwargs)

        if shipping_status == "true":
            order.recibido = True
            order.save()
            messages.success(request, "¡Orden marcada como recibida!")
        else:
            messages.warning(request, "Acción no válida.")

        return self.get(request, *args, **kwargs)

    
@add_group_name_to_context
class ComprasUsuarioView(UserPassesTestMixin, LoginRequiredMixin, TemplateView):
    template_name = "payment/compras_usuario.html"

    def test_func(self):
        # Verifica si el usuario es superusuario
        return self.request.user.is_authenticated

    def handle_no_permission(self):
        # Redirige a la página de error con un mensaje
        messages.error(self.request, "Access Denied")
        return redirect("error")

    def get_context_data(self, **kwargs):
        # Obtiene el contexto base
        context = super().get_context_data(**kwargs)
        # Obtiene la orden y los elementos de la orden
        pk = self.kwargs.get('pk')  # Obtiene el ID de la orden desde la URL
        context["order"] = Order.objects.get(id=pk)
        context["items"] = OrderItem.objects.filter(order=pk)
        n= OrderItem.objects.filter(order=pk)
        
        return context

#funcion para el envio de correos desde info de pedidos
def contact(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        subject = request.POST['subject']
        message = request.POST['message']
        
        # Aquí pasamos los datos que enviamos al correo
        template = render_to_string('html_para_correos/email-template.html', {
            'name': name,
            'email': email,
            'subject': subject,
            'message': message,
            'order_id': request.POST['order_id'],
            'amount_paid': request.POST['amount_paid'],
            'shipping_address': request.POST['shipping_address'],
            'date_ordered': request.POST['date_ordered'],
            'date_shipped': request.POST.get('date_shipped', None),  # Evita KeyError si no existe
            'products': request.POST.getlist('products')  # Captura múltiples productos correctamente
        })
        staff_users = User.objects.filter(is_staff=True)
        admin_emails = [user.email for user in staff_users]  # Obtener los correos de los staff

        # Agregar correos adicionales si es necesario
        admin_emails.extend([ "basuradecorreo2002@gmail.com"])
        emailSender = EmailMessage(
            subject,
            template,
            settings.EMAIL_HOST_USER,
            to=admin_emails
        )
        emailSender.content_subtype = 'html'
        emailSender.fail_silently = False
        emailSender.send()

        messages.success(request, 'El correo electrónico se envió correctamente')
        return redirect('compras')

class GenerarPDFReciboView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        if request.user.is_superuser:
            order = get_object_or_404(Order, id=pk)
        else:
            order = get_object_or_404(Order, id=pk, user=request.user)
        items = OrderItem.objects.filter(order=order)

        # URL absoluta del logo para que WeasyPrint la resuelva
        logo_url = request.build_absolute_uri(static('logo/LogoFerrer.png'))

        # Construir lista de items con posible imagen absoluta del producto
        items_data = []
        for it in items:
            prod = it.product
            prod_image_url = None
            if prod:
                # preferir imagen1
                for img_field in ('imagen1', 'imagen2', 'imagen3', 'imagen4'):
                    img = getattr(prod, img_field, None)
                    if img and getattr(img, 'url', None):
                        try:
                            prod_image_url = request.build_absolute_uri(img.url)
                            break
                        except Exception:
                            prod_image_url = None
            items_data.append({'item': it, 'product_image': prod_image_url})

        html_string = render_to_string(
            'payment/recibo_pdf.html',
            {'order': order, 'items_data': items_data, 'logo_url': logo_url}
        )
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="recibo_{order.id}.pdf"'
        HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf(response)
        return response
    
#final 