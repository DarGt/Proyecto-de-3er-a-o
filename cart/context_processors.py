from .cart import Cart
#procesador de contexto para q el carro funcione en todas las paginas
def cart(request):
    #devolver los datos prede
    return {"cart":Cart(request)}