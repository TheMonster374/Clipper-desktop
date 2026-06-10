import json


def cargarReglas():
    archivo = open('rules.json', 'r')
    rules = json.load(archivo)
    archivo.close()

    return rules

rules = cargarReglas()