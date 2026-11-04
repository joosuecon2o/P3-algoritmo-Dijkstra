# Módulo de grafos que contiene las clases Nodo, Arista y Grafo, así como funciones para generar grafos específicos.
# Importa las clases Nodo, Arista y Grafo desde sus respectivos módulos.
import heapq
import itertools
import random
import sys

from .nodo import Nodo
from .arista import Arista

# Importa la clase Grafo desde su módulo.
class Grafo:

    # Inicializa un nuevo grafo
    def __init__(self, dirigido=False):
        self.dirigido = dirigido
        self.nodos = {}
        self.aristas = []
        self._vecinos = {}
        self._grado = {}
        self._pesos = {}

    # Agrega un nodo al grafo
    def agregar_nodo(self, id_nodo):
        if id_nodo not in self.nodos:
            self.nodos[id_nodo] = Nodo(id_nodo)
            self._vecinos[id_nodo] = set()
            self._grado[id_nodo] = 0
        return self.nodos[id_nodo]

    # Verifica si existe una arista entre dos nodos
    def existe_arista(self, id_nodo1, id_nodo2):
        return id_nodo2 in self._vecinos.get(id_nodo1, ())

    # Agrega una arista entre dos nodos
    def agregar_arista(self, id_nodo1, id_nodo2, peso=None):
        self.agregar_nodo(id_nodo1)
        self.agregar_nodo(id_nodo2)
        if id_nodo1 == id_nodo2 or self.existe_arista(id_nodo1, id_nodo2):
            return None
        arista = Arista(self.nodos[id_nodo1], self.nodos[id_nodo2], self.dirigido, peso)
        self.aristas.append(arista)
        self._vecinos[id_nodo1].add(id_nodo2)
        self._pesos[(id_nodo1, id_nodo2)] = peso
        if not self.dirigido:
            self._vecinos[id_nodo2].add(id_nodo1)
            self._pesos[(id_nodo2, id_nodo1)] = peso
        self._grado[id_nodo1] += 1
        self._grado[id_nodo2] += 1
        return arista

    # Obtiene el peso de la arista (id_nodo1, id_nodo2); None si la arista no tiene peso
    def peso(self, id_nodo1, id_nodo2):
        return self._pesos[(id_nodo1, id_nodo2)]

    # Asigna a cada arista un peso aleatorio uniforme en [minimo, maximo]
    def asignar_pesos_aleatorios(self, minimo=1, maximo=100, decimales=2):
        """
        Asigna a cada arista del grafo un peso aleatorio, redondeado a
        'decimales' cifras, tomado de una distribución uniforme en [minimo, maximo].
        :param minimo: peso mínimo (>= 0, porque Dijkstra no admite pesos negativos)
        :param maximo: peso máximo
        :param decimales: número de decimales del peso
        """
        for arista in self.aristas:
            u, v = arista.origen.id_nodo, arista.destino.id_nodo
            arista.peso = round(random.uniform(minimo, maximo), decimales)
            self._pesos[(u, v)] = arista.peso
            if not self.dirigido:
                self._pesos[(v, u)] = arista.peso

    # Obtiene los vecinos de un nodo
    def vecinos(self, id_nodo):
        return self._vecinos.get(id_nodo, set())
    def grado(self, id_nodo):
        return self._grado[id_nodo]

    # Verifica si todos los nodos están conectados (sin nodos aislados ni componentes sueltas)
    def es_conexo(self):
        if not self.nodos:
            return True
        vecinos_sin_direccion = {id_nodo: set() for id_nodo in self.nodos}
        for arista in self.aristas:
            vecinos_sin_direccion[arista.origen.id_nodo].add(arista.destino.id_nodo)
            vecinos_sin_direccion[arista.destino.id_nodo].add(arista.origen.id_nodo)
        inicio = next(iter(self.nodos))
        visitados = {inicio}
        pila = [inicio]
        while pila:
            actual = pila.pop()
            for vecino in vecinos_sin_direccion[actual]:
                if vecino not in visitados:
                    visitados.add(vecino)
                    pila.append(vecino)
        return len(visitados) == len(self.nodos)

    # Búsqueda a lo ancho (BFS)
    def BFS(self, s):
        """
        Calcula el árbol inducido por la búsqueda a lo ancho desde s.
        Explora el grafo por capas: L[0] = {s} y L[i+1] contiene los nodos no
        descubiertos que tienen una arista con algún nodo de L[i]. Cada nodo
        nuevo se une en el árbol con el nodo de la capa anterior que lo descubrió.
        :param s: identificador del nodo fuente
        :return: árbol BFS (Grafo) con raíz en s
        """
        self._validar_fuente(s)
        arbol = Grafo(self.dirigido)
        arbol.agregar_nodo(s)
        descubierto = {s}
        capa = [s]
        while capa:
            siguiente_capa = []
            for u in capa:
                for v in self._vecinos[u]:
                    if v not in descubierto:
                        descubierto.add(v)
                        arbol.agregar_arista(u, v)
                        siguiente_capa.append(v)
            capa = siguiente_capa
        return arbol

    # Búsqueda en profundidad recursiva (DFS)
    def DFS_R(self, s):
        """
        Calcula el árbol inducido por la búsqueda en profundidad recursiva desde s.
        DFS(u) marca u como explorado y, por cada arista (u, v) con v no
        explorado, agrega (u, v) al árbol e invoca DFS(v).
        :param s: identificador del nodo fuente
        :return: árbol DFS (Grafo) con raíz en s
        """
        self._validar_fuente(s)
        arbol = Grafo(self.dirigido)
        arbol.agregar_nodo(s)
        # La profundidad de la recursión puede llegar al número de nodos
        limite_original = sys.getrecursionlimit()
        sys.setrecursionlimit(max(limite_original, len(self.nodos) + 100))
        try:
            self._dfs_recursivo(s, set(), arbol)
        finally:
            sys.setrecursionlimit(limite_original)
        return arbol

    # Paso recursivo de DFS_R
    def _dfs_recursivo(self, u, explorado, arbol):
        explorado.add(u)
        for v in self._vecinos[u]:
            if v not in explorado:
                arbol.agregar_arista(u, v)
                self._dfs_recursivo(v, explorado, arbol)

    # Búsqueda en profundidad iterativa (DFS)
    def DFS_I(self, s):
        """
        Calcula el árbol inducido por la búsqueda en profundidad iterativa desde s.
        Sustituye la recursión por una pila explícita: cada elemento guarda un
        nodo y el iterador de sus vecinos pendientes, igual que lo haría la pila
        de llamadas de DFS_R. Por eso ambos métodos producen el mismo árbol.
        :param s: identificador del nodo fuente
        :return: árbol DFS (Grafo) con raíz en s
        """
        self._validar_fuente(s)
        arbol = Grafo(self.dirigido)
        arbol.agregar_nodo(s)
        explorado = {s}
        pila = [(s, iter(self._vecinos[s]))]
        while pila:
            u, pendientes = pila[-1]
            for v in pendientes:
                if v not in explorado:
                    explorado.add(v)
                    arbol.agregar_arista(u, v)
                    pila.append((v, iter(self._vecinos[v])))
                    break
            else:
                # u ya no tiene vecinos sin explorar: se regresa a su padre
                pila.pop()
        return arbol

    # Algoritmo de Dijkstra
    def Dijkstra(self, s):
        """
        Calcula el árbol de caminos más cortos desde s con el algoritmo de Dijkstra.
        S es el conjunto de nodos explorados, cuya distancia a s ya es definitiva.
        En cada paso se extrae de la cola de prioridad el nodo no explorado con la
        menor distancia tentativa (delmin), se agrega a S y se relajan sus aristas:
        si d(u) + l(u, v) mejora la distancia de v, se actualiza la distancia y el
        padre de v (decrease key, implementado insertando una nueva entrada en la
        cola y descartando después las entradas obsoletas).
        Las aristas sin peso cuentan como peso 1.
        :param s: identificador del nodo fuente
        :return: árbol de caminos más cortos (Grafo). Cada nodo se llama
                 "nodo (distancia)", por ejemplo "nodo_2 (22.45)", y cada arista
                 (padre, hijo) conserva su peso.
        """
        self._validar_fuente(s)
        for arista in self.aristas:
            if arista.peso is not None and arista.peso < 0:
                raise ValueError("Dijkstra no admite aristas con peso negativo")

        distancia = {s: 0}
        padre = {s: None}
        explorados = []         # nodos en el orden en que entran a S
        en_s = set()
        desempate = itertools.count()   # evita comparar identificadores de nodos
        cola = [(0, next(desempate), s)]
        while cola:
            d_u, _, u = heapq.heappop(cola)          # delmin
            if u in en_s:
                continue                             # entrada obsoleta
            en_s.add(u)
            explorados.append(u)
            for v in self._vecinos[u]:
                if v in en_s:
                    continue
                peso = self._pesos[(u, v)]
                nueva = d_u + (1 if peso is None else peso)
                if v not in distancia or nueva < distancia[v]:
                    distancia[v] = nueva             # decrease key
                    padre[v] = u
                    heapq.heappush(cola, (nueva, next(desempate), v))

        arbol = Grafo(self.dirigido)
        etiqueta = {v: f"{v} ({distancia[v]:.2f})" for v in explorados}
        for v in explorados:
            arbol.agregar_nodo(etiqueta[v])
            if padre[v] is not None:
                arbol.agregar_arista(etiqueta[padre[v]], etiqueta[v], self._pesos[(padre[v], v)])
        return arbol

    # Verifica que el nodo fuente exista en el grafo
    def _validar_fuente(self, s):
        if s not in self.nodos:
            raise KeyError(f"El nodo fuente {s!r} no existe en el grafo")

    # Guarda el grafo en un archivo en formato Graphviz; el peso de cada arista,
    # si lo tiene, se escribe en el atributo weight
    def guardar_graphviz(self, archivo):
        conector = "->" if self.dirigido else "--"
        tipo = "digraph" if self.dirigido else "graph"
        with open(archivo, "w") as f:
            f.write(f"{tipo} G {{\n")
            for id_nodo in self.nodos:
                f.write(f'    "{id_nodo}";\n')
            for arista in self.aristas:
                atributos = "" if arista.peso is None else f" [weight={arista.peso}]"
                f.write(f'    "{arista.origen.id_nodo}" {conector} "{arista.destino.id_nodo}"{atributos};\n')
            f.write("}\n")

    # Devuelve el número de nodos en el grafo
    def __len__(self):
        return len(self.nodos)

    # Representación del grafo como cadena
    def __repr__(self):
        return f"Grafo(nodos={len(self.nodos)}, aristas={len(self.aristas)}, dirigido={self.dirigido})"
