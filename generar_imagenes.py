# Genera las imágenes PNG de los grafos generados y de los árboles de caminos
# más cortos a partir de los archivos .gv, usando Graphviz (https://graphviz.org).
import os
import re
import shutil
import subprocess

CARPETAS = {
    os.path.join("gv", "generados"): os.path.join("imagenes", "generados"),
    os.path.join("gv", "calculados"): os.path.join("imagenes", "calculados"),
}
RUTA_GRAPHVIZ_WINDOWS = r"C:\Program Files\Graphviz\bin"
MAX_NODOS_CON_ETIQUETA = 30


# Busca un programa de Graphviz en el PATH o en la ruta de instalación de Windows
def programa_graphviz(nombre):
    ruta = shutil.which(nombre)
    if ruta is None:
        ruta = shutil.which(nombre, path=RUTA_GRAPHVIZ_WINDOWS)
    if ruta is None:
        raise RuntimeError(f"No se encontró '{nombre}'; instala Graphviz y agrégalo al PATH")
    return ruta


# Devuelve los identificadores de los nodos tal como aparecen en el .gv (con comillas)
def leer_nodos(texto):
    return [l.strip()[:-1] for l in texto.splitlines()[1:]
            if l.strip().endswith(";") and "--" not in l and "->" not in l]


# Agrega estilo al texto .gv sin modificar el archivo original; la raíz va en rojo.
# - Árboles de Dijkstra: se muestran todas las etiquetas "nodo (distancia)".
# - Grafos generados pequeños: nodos con etiqueta y el peso escrito en cada arista.
# - Grafos generados grandes: nodos como puntos, sin etiquetas.
def dar_estilo(texto, es_arbol):
    lineas = texto.splitlines()
    nodos = leer_nodos(texto)
    pequeno = len(nodos) <= MAX_NODOS_CON_ETIQUETA

    tamano = "10,10"
    if es_arbol and pequeno:
        estilo_nodo = 'node [shape=box, style="rounded,filled", fillcolor="#dbe9f6", fontsize=10, height=0.3];'
    elif es_arbol:
        estilo_nodo = 'node [shape=plaintext, fontsize=7, height=0.1, width=0.1, margin=0];'
        tamano = "40,40"
    elif pequeno:
        estilo_nodo = 'node [shape=circle, fontsize=9, width=0.45, fixedsize=true, style=filled, fillcolor="#dbe9f6"];'
    else:
        estilo_nodo = 'node [shape=point, width=0.08, color="#1f4e79"];'

    estilo = [
        f'graph [overlap=false, splines=false, outputorder=edgesfirst, size="{tamano}", dpi=100, bgcolor=white];',
        estilo_nodo,
        'edge [color="#7f7f7f", penwidth=0.8, fontsize=8, fontcolor="#a0522d"];',
    ]
    if nodos:
        if es_arbol and not pequeno:
            estilo.append(f'{nodos[0]} [root=true, fontcolor=red, fontsize=14];')
        elif es_arbol or pequeno:
            estilo.append(f'{nodos[0]} [root=true, color=red, fillcolor=red];')
        else:
            estilo.append(f'{nodos[0]} [root=true, color=red, fillcolor=red, style=filled, width=0.2];')

    cuerpo = "\n".join(lineas[1:])
    if pequeno:
        # Muestra el peso de cada arista como etiqueta
        cuerpo = re.sub(r"\[weight=([0-9.]+)\]", r'[weight=\1, label="\1"]', cuerpo)
    return "\n".join([lineas[0]] + estilo) + "\n" + cuerpo + "\n"


# Árboles: twopi, que coloca la raíz al centro; grafos generados: sfdp
def dibujar(ruta_gv, ruta_png):
    es_arbol = os.path.basename(ruta_gv).endswith("_Dijkstra.gv")
    with open(ruta_gv) as f:
        texto = f.read()
    programa = programa_graphviz("twopi" if es_arbol else "sfdp")
    comando = [programa, "-Tpng", "-o", ruta_png]
    subprocess.run(comando, input=dar_estilo(texto, es_arbol).encode("utf-8"), check=True)
    print(ruta_png)


def generar_todas():
    for carpeta_gv, carpeta_png in CARPETAS.items():
        os.makedirs(carpeta_png, exist_ok=True)
        for archivo in sorted(os.listdir(carpeta_gv)):
            if archivo.endswith(".gv"):
                dibujar(os.path.join(carpeta_gv, archivo),
                        os.path.join(carpeta_png, archivo[:-3] + ".png"))


if __name__ == "__main__":
    generar_todas()
