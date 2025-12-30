from guardar.models import Producto
from accounts.models import Usuario

class Cart():
    def __init__(self, request):
        self.session = request.session
        # Obtendremos la clave de la sesión si existe
        self.request = request
        cart = self.session.get("session_key")

        # Si el usuario es nuevo, se crea una nueva clave para el carrito
        if 'session_key' not in request.session:
            cart = self.session['session_key'] = {}
        self.cart = cart
  
        #self.session.modified = True  # Marcar la sesión como modificada
        
    def db_add(self,product, quantity):
        product_id = str(product)
        product_qty = str(quantity)
        
        if product_id in self.cart:
            pass
        else:
            #self.cart[product_id]={"price":str(product.precio_venta)}
            self.cart[product_id] = int(product_qty)
        
        self.session.modified = True
        
        #determinamos si el usuario a iniciado sesion
        if self.request.user.is_authenticated:
            #octener el perfil del usuario
            current_user = Usuario.objects.filter(user__id= self.request.user.id)
            carty = str(self.cart)
            carty = carty.replace("\'", "\"")
            #guardar carty en el Usuario
            current_user.update(old_cart = str(carty))
        
        

    def add(self, product, quantity):
        product_id = str(product.id_producto)
        product_qty = str(quantity)
        
        if product_id in self.cart:
            pass
        else:
            #self.cart[product_id]={"price":str(product.precio_venta)}
            self.cart[product_id] = int(product_qty)
        
        self.session.modified = True
        
        #determinamos si el usuario a iniciado sesion
        if self.request.user.is_authenticated:
            #octener el perfil del usuario
            current_user = Usuario.objects.filter(user__id= self.request.user.id)
            carty = str(self.cart)
            carty = carty.replace("\'", "\"")
            #guardar carty en el Usuario
            current_user.update(old_cart = str(carty))

    # función que permite ver la cantidad de producto
    def __len__(self):
        return len(self.cart.values())

    # función que permite ver los productos
    def get_prods(self):
        # obtener los id del carrito
        product_ids = self.cart.keys()
        # obtener los id de la bd
        products = Producto.objects.filter(id_producto__in=product_ids)
        
        return products

    def get_quants(self):
        quantities = self.cart
        return quantities

    def update(self, product, quantity):
        # Convertir el ID del producto a cadena y la cantidad a entero
        product_id = str(product)
        product_qty = int(quantity)
    
        # Actualizar el carrito con el producto y su cantidad
        self.cart[product_id] = product_qty
    
        # Marcar la sesión como modificada para guardar cambios
        self.session.modified = True
        
        if self.request.user.is_authenticated:
            #octener el perfil del usuario
            current_user = Usuario.objects.filter(user__id= self.request.user.id)
            carty = str(self.cart)
            carty = carty.replace("\'", "\"")
            #guardar carty en el Usuario
            current_user.update(old_cart = str(carty))
        # Retornar el carrito actualizado
        return self.cart

    # función de borrado
    def delete(self, product):
        product_id = str(product)
        # borrar diccionario
        if product_id in self.cart:
            del self.cart[product_id]
        
        self.session.modified = True
        
        if self.request.user.is_authenticated:
            #octener el perfil del usuario
            current_user = Usuario.objects.filter(user__id= self.request.user.id)
            carty = str(self.cart)
            carty = carty.replace("\'", "\"")
            #guardar carty en el Usuario
            current_user.update(old_cart = str(carty))
        
    def cart_total(self):
        product_ids = self.cart.keys()
        
        products= Producto.objects.filter(id_producto__in=product_ids)
        
        quatities = self.cart
        total = 0
        for key , value in quatities.items():
            key = int(key)
            for product in products:
                if product.id_producto == key:
                    if product.is_sale:
                        
                        total = total +(product.sale_price * value)
                        
                    else:
                        total = total +(product.precio_venta * value)
                    
        return total
        
        