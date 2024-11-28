def es_sano(calorias: int, vegetariano: bool) -> bool:
    return calorias < 100 or vegetariano

def calcular_calorias(calorias: list[int]) -> float:
    return round(sum(calorias) * 0.95, 2)

def calcular_costo(ingredientes: list[dict]) -> int:
    return sum(ing['precio'] for ing in ingredientes)

def calcular_rentabilidad(precio: int, ingredientes: list[dict]) -> int:
    return precio - calcular_costo(ingredientes)

def producto_mas_rentable(productos: list[dict]) -> str:
    return max(productos, key=lambda p: p['rentabilidad'])['nombre']
