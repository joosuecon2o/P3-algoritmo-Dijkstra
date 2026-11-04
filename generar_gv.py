import math
import os

from grafos import (
    grafo_erdos_renyi,
    grafo_gilbert,
    grafo_geografico,
    grafo_barabasi_albert,
    grafo_dorogovtsev_mendes,
)

# "Pocos" y "muchos" nodos para cada generador aleatorio
TAMANOS = [30, 500]
PESO_MINIMO = 1
PESO_MAXIMO = 100
CARPETA_GENERADOS = os.path.join("gv", "generados")
CARPETA_CALCULADOS = os.path.join("gv", "calculados")
MAX_INTENTOS = 1000


# Los parámetros están un poco por encima del umbral de conectividad (ln n / n)
# para que casi siempre salga conexo; si no, se vuelve a generar.
def generar_todos():
    os.makedirs(CARPETA_GENERADOS, exist_ok=True)
    os.makedirs(CARPETA_CALCULADOS, exist_ok=True)

    for n in TAMANOS:
        m = round(n * (math.log(n) + 2) / 2)
        procesar(lambda: grafo_erdos_renyi(n, m), f"1_Erdos_Renyi_n{n}")

        p = (math.log(n) + 3) / n
        procesar(lambda: grafo_gilbert(n, p), f"2_Gilbert_n{n}")

        r = math.sqrt((math.log(n) + 4) / (math.pi * n))
        procesar(lambda: grafo_geografico(n, r), f"3_Geografico_n{n}")

        procesar(lambda: grafo_barabasi_albert(n, 4), f"4_Barabasi_Albert_n{n}")

        procesar(lambda: grafo_dorogovtsev_mendes(n), f"5_Dorogovtsev_Mendes_n{n}")


def generar_conexo(generador):
    for _ in range(MAX_INTENTOS):
        grafo = generador()
        if grafo.es_conexo():
            return grafo
    raise RuntimeError(f"No se obtuvo un grafo conexo en {MAX_INTENTOS} intentos")


# Genera un grafo conexo, le asigna pesos aleatorios a sus aristas, lo guarda y
# guarda su árbol de caminos más cortos. El nodo fuente es el nodo 0.
def procesar(generador, nombre):
    grafo = generar_conexo(generador)
    grafo.asignar_pesos_aleatorios(PESO_MINIMO, PESO_MAXIMO)
    guardar(grafo, os.path.join(CARPETA_GENERADOS, f"{nombre}.gv"))

    s = next(iter(grafo.nodos))
    guardar(grafo.Dijkstra(s), os.path.join(CARPETA_CALCULADOS, f"{nombre}_Dijkstra.gv"))


def guardar(grafo, ruta):
    grafo.guardar_graphviz(ruta)
    print(f"{ruta}: {len(grafo.nodos)} nodos, {len(grafo.aristas)} aristas")


if __name__ == "__main__":
    generar_todos()
