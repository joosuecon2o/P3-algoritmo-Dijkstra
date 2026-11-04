# Algoritmo de Dijkstra

Proyecto 3 de Diseño y Análisis de Algoritmos: a partir de la biblioteca de grafos del [Proyecto 1](https://github.com/joosuecon2o/P1-biblioteca-grafos), ampliada en el [Proyecto 2](https://github.com/joosuecon2o/P2-algoritmos-BFS-DFS), se implementa el algoritmo de Dijkstra. Dado un nodo fuente `s`, calcula el árbol de caminos más cortos.

## Método `Dijkstra(self, s)`

Está en `grafos/grafo.py` y sigue el algoritmo visto en clase:

1. `S` es el conjunto de nodos explorados, cuya distancia a `s` ya es definitiva. Inicia vacío, con `d(s) = 0`.
2. Se extrae de la cola de prioridad el nodo `u` no explorado con la menor distancia tentativa (*delmin*) y se agrega a `S`.
3. Para cada arista `(u, v)` con `v` fuera de `S`, si `d(u) + l(u, v)` mejora la distancia de `v`, se actualizan la distancia y el padre de `v` (*decrease key*).
4. Se repite hasta vaciar la cola.

La cola de prioridad es un montículo (`heapq`). El *decrease key* se implementa insertando una nueva entrada y descartando después las obsoletas, por lo que el costo es O((n + m) log n).

El método devuelve el árbol como un nuevo `Grafo`. Cada nodo se llama `"nodo (distancia)"`, con la distancia al origen redondeada a dos decimales; por ejemplo, el nodo `2` a distancia 22.45 aparece como `"2 (22.45)"`. Cada arista (padre, hijo) conserva su peso. Lanza `ValueError` si hay aristas con peso negativo y `KeyError` si `s` no existe. Las aristas sin peso cuentan como peso 1.

### Cambios en la clase `Grafo`

- `agregar_arista(u, v, peso)` guarda el peso de la arista, y `peso(u, v)` lo consulta.
- `asignar_pesos_aleatorios(minimo, maximo)` asigna a cada arista un peso uniforme en `[minimo, maximo]`, con dos decimales.
- `guardar_graphviz` escribe el peso de cada arista en el atributo `weight`, por ejemplo `"0" -- "26" [weight=11.07];`.
- Se conservan los métodos `BFS`, `DFS_R` y `DFS_I` del Proyecto 2.

## Estructura

- `grafos/` — código fuente de la biblioteca (`nodo.py`, `arista.py`, `grafo.py` y `generadores.py`)
- `generar_gv.py` — genera los grafos, les asigna pesos y calcula sus árboles de caminos más cortos
- `generar_imagenes.py` — dibuja todos los `.gv` con Graphviz
- `gv/generados/` — 10 grafos: los 5 generadores aleatorios × "pocos" (30) y "muchos" (500) nodos
- `gv/calculados/` — 10 árboles de Dijkstra, uno por grafo generado
- `imagenes/generados/` y `imagenes/calculados/` — una imagen PNG por cada archivo `.gv`

Los generadores aleatorios son Erdős–Rényi, Gilbert, geográfico simple, Barabási–Albert y Dorogovtsev–Mendes. La malla no se usa porque no es aleatoria.

## Uso

```python
from grafos import grafo_gilbert

g = grafo_gilbert(30, 0.2)
g.asignar_pesos_aleatorios(1, 100)

arbol = g.Dijkstra(0)
print(next(iter(arbol.nodos)))   # 0 (0.00): el nodo fuente, a distancia 0
arbol.guardar_graphviz("dijkstra.gv")
```

## Generar los archivos

```
python generar_gv.py
python generar_imagenes.py
```

`generar_gv.py` vuelve a generar cada grafo hasta obtener uno conexo, de modo que el árbol abarca todos los nodos. Los pesos son aleatorios entre 1 y 100, y el nodo fuente es el `0`.

`generar_imagenes.py` requiere [Graphviz](https://graphviz.org). Los grafos generados se dibujan con `sfdp`; en los de 30 nodos se escribe el peso sobre cada arista. Los árboles se dibujan con `twopi`, con la raíz (en rojo) al centro y la etiqueta `nodo (distancia)` en cada nodo. Las imágenes de los árboles de 500 nodos son grandes, para que las etiquetas se lean al hacer zoom.

El código está probado con Python 3.6.8, la versión que pide el curso.
