from django.urls import path
from . import views
from .views import CheckoutView,BillingInfoView, NotShippedDashView,ShippedDashView,OrderDetailView, PaymentCompletedView,PaymentCanceledView,PaymentProcessView,ComprasView,ComprasUsuarioView,contact, GenerarPDFReciboView
from django.contrib.auth.decorators import login_required
urlpatterns = [
    path('payment_success/', views.payment_succes, name='payment_success'),
    path('checkout/',CheckoutView.as_view(), name='checkout'),
    path('billing_info/', BillingInfoView.as_view(), name='billing_info'),
    path('process_order/', views.process_order, name='process_order'),
    path('shipped_dash/', ShippedDashView.as_view(), name='shipped_dash'),#para productos enviado s
    path('not_shipped_dash/', NotShippedDashView.as_view(), name='not_shipped_dash'),#para no enviados
    path('orders/<int:pk>', OrderDetailView.as_view(), name='orders'),#para no enviados
    path('process/', PaymentProcessView.as_view(), name='process'),
    path('completed/', PaymentCompletedView.as_view(), name='completed'),
    path('canceled/', PaymentCanceledView.as_view(), name='canceled'),
    path('compras/', login_required(ComprasView.as_view()), name='compras'),
    path('compras_usuario/<int:pk>', login_required(ComprasUsuarioView.as_view()), name='compras_usuario'),
    path('contact', login_required(contact), name='contact'),
    path('recibo/pdf/<int:pk>/', GenerarPDFReciboView.as_view(), name='generar_pdf_recibo'),
]