from models.ingrediente import Ingrediente

class Base(Ingrediente):
    def __init__(self, nombre, precio, calorias, inventario, es_vegetariano, sabor):
        super().__init__(nombre, precio, calorias, inventario, es_vegetariano)
        self.sabor = sabor

    def abastecer(self, cantidad=5):
        """
        Incrementa el inventario en la cantidad especificada (por defecto, 5 unidades).
        """
        self.inventario += cantidad

    # Getter y Setter para sabor
    def get_sabor(self):
        return self.sabor

    def set_sabor(self, sabor):
        self.sabor = sabor
