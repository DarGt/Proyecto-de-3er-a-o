from django.urls import path, re_path
from .views import Principal, Carrito, Informacion,  Registro, cerrar_sesion, PerfilView, Error_Permiso, CambioContraseña, Detalles_Usuario_admin, superuser_edit, AddUserview,  eliminar_usuario, ProductoDetailView, CategoryListView, CategorySummaryView, search,CustomLoginView,LoginUserView,administrativos,PasswordResetView, PasswordResetDoneView,  PasswordResetConfirmView,PasswordResetCompleteView,EliminaUsuario2View,agregar_comentario,editar_comentario,eliminar_comentario
from django.contrib.auth.decorators import login_required, user_passes_test
from . import views
def not_authenticated(user):
    return not user.is_authenticated

urlpatterns = [
    path("", Principal.as_view(), name="index"),
    path("carrito/", Carrito.as_view(), name="carrito"),
    path("login/",CustomLoginView.as_view(), name="login"),
    path("informacion/", Informacion.as_view(), name="informacion"),
    path("register/", Registro.as_view(), name="register"),
    path("cerrar_sesion/", cerrar_sesion, name="cerrar_sesion"),
    path("perfil/", login_required(PerfilView.as_view()), name="perfil"),
    path("error/", login_required(Error_Permiso.as_view()), name="error"),
    path("password/", login_required(CambioContraseña.as_view()), name="password"),
    path("user_detail/<int:pk>/", login_required(Detalles_Usuario_admin.as_view()), name="user_detail"),
    path("superuser_edit/<int:user_id>/", login_required(superuser_edit), name="superuser_edit"),
    path("agregar_usuario/", login_required(AddUserview.as_view()), name="agregar_usuario"),
    
    path('eliminar_usuario/<int:user_id>/', login_required(eliminar_usuario), name='eliminar_usuario'),
    path('producto/<int:pk>/', ProductoDetailView.as_view(), name='producto_detail'),
    path('producto/<int:id_producto>/comentario/', views.agregar_comentario, name='agregar_comentario'),
    path('category/<str:foo>/', CategoryListView.as_view(), name='category'),
    path('category_summary/', CategorySummaryView.as_view(), name='category_summary'),
        path('ini/', user_passes_test(not_authenticated, login_url="perfil")(LoginUserView.as_view()), name='ini'),
    path('search/', search, name='search'),
    path('administrativos/', views.administrativos, name='administrativos'),
    
    
    path(
        'reset/password_reset/', 
        PasswordResetView.as_view(
            template_name='registration/password_reset_forms.html',
            extra_context={'email_template_name': 'registration/password_reset_email.html'}
        ), 
        name='password_reset'
    ),
    
    re_path(r'^reset/(?P<uidb64>[0-9A-za-z_\-]+)/(?P<token>.+)/$', PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirms.html'), name = 'password_reset_confirm'),
    path('reset/done',PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html') , name = 'password_reset_complete'),
    
    path('elimina/', EliminaUsuario2View.as_view(), name='elimina'),
    path('producto/<int:id_producto>/editar-comentario/', editar_comentario, name='editar_comentario'),
    path('producto/<int:id_producto>/eliminar-comentario/', eliminar_comentario, name='eliminar_comentario'),
    path('like-toggle/<int:id_producto>/', views.like_toggle, name='like_toggle'),

]
    
    

