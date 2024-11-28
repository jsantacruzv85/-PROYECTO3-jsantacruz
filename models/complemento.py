from models.ingrediente import Ingrediente

class Complemento(Ingrediente):
    def __init__(self, nombre, precio, calorias, inventario, es_vegetariano):
        super().__init__(nombre, precio, calorias, inventario, es_vegetariano)

    def abastecer(self, cantidad=10):
        """
        Incrementa el inventario en la cantidad especificada (por defecto, 10 unidades).
        """
        self.inventario += cantidad

    def renovar_inventario(self):
        """
        Reduce el inventario a 0.
        """
        self.inventario = 0
