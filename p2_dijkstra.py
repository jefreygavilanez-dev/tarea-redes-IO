"""
=====================================================================
P2. ALGORITMO DE DIJKSTRA (ruta más corta desde un origen)
=====================================================================
Capítulo 6 - Modelos de redes (Investigación Operativa)

PROBLEMA
    En una red DIRIGIDA con longitudes d_ij >= 0, hallar la ruta más
    corta del nodo 1 a todos los demás nodos.

RED DEL EJERCICIO (arcos dirigidos i -> j = longitud)
    1->2 = 5    1->3 = 2    3->2 = 1    2->4 = 4    2->5 = 9
    3->4 = 8    3->5 = 12   4->5 = 3    4->6 = 7    5->6 = 2

ALGORITMO (etiquetas [u_j, i])
    Cada nodo j recibe una etiqueta [u_j, i]:
        u_j : distancia más corta conocida desde el origen hasta j.
        i   : nodo inmediatamente anterior en esa ruta (predecesor).
    Las etiquetas son TEMPORALES (pueden mejorar) o PERMANENTES.

    Paso 0: el origen tiene etiqueta permanente [0, -].
    Paso i: (a) desde el nodo i recién hecho permanente, para cada
                sucesor j aún temporal se calcula u_i + d_ij y se
                reemplaza la etiqueta SOLO si mejora (es menor).
            (b) entre todas las etiquetas temporales, la de menor u
                se vuelve permanente.
    Termina cuando todos los nodos son permanentes. Las rutas se
    reconstruyen hacia atrás siguiendo los predecesores.

    Requiere longitudes NO negativas.

SALIDA ESPERADA
    u = (0, 3, 2, 7, 10, 12);  ruta 1->6: 1-3-2-4-5-6

DEPENDENCIAS
    pip install networkx
"""
import math
import networkx as nx

# ---------------------------------------------------------------------
# DATOS: diccionario {(origen, destino): longitud}
# ---------------------------------------------------------------------
arcos = {(1, 2): 5, (1, 3): 2, (3, 2): 1, (2, 4): 4, (2, 5): 9,
         (3, 4): 8, (3, 5): 12, (4, 5): 3, (4, 6): 7, (5, 6): 2}

# Lista ordenada de nodos deducida de los extremos de los arcos.
nodos = sorted({n for a in arcos for n in a})


def dijkstra(nodos, arcos, s):
    """
    Ejecuta Dijkstra desde el nodo origen `s` e imprime la tabla de
    etiquetas iteración por iteración.

    Retorna
    -------
    (u, pred)
        u    : dict {nodo: distancia mínima desde s}.
        pred : dict {nodo: predecesor en la ruta más corta}.
    """
    # Distancias iniciales: infinito (aún no alcanzado) salvo el origen.
    u = {n: math.inf for n in nodos}
    # Predecesor de cada nodo (se llena al mejorar etiquetas).
    pred = {n: None for n in nodos}
    u[s], pred[s] = 0, "-"      # etiqueta del origen: [0, -]
    perm = []                   # nodos con etiqueta permanente (en orden)

    def fila(it):
        """Imprime una fila de la tabla de etiquetas de la iteración it."""
        celdas = []
        for n in nodos:
            if n in perm and n != perm[-1]:
                # Nodo hecho permanente en una iteración anterior.
                celdas.append("  ok  ")
            elif u[n] == math.inf:
                # Nodo todavía no alcanzado: sin etiqueta.
                celdas.append("   -  ")
            else:
                # Etiqueta [u_j, predecesor] (temporal o recién permanente).
                celdas.append(f"[{u[n]},{pred[n]}]".center(6))
        print(f"{it:>3} | " + " | ".join(celdas))

    # Encabezado de la tabla y fila de la iteración 0.
    print("It. | " + " | ".join(f"N{n}".center(6) for n in nodos))
    it = 0
    fila(it)

    # Bucle principal: un nodo se vuelve permanente por iteración.
    while len(perm) < len(nodos):
        # Candidatos: nodos no permanentes que ya tienen etiqueta finita.
        temporales = [n for n in nodos if n not in perm and u[n] < math.inf]
        if not temporales:
            break               # nodos inalcanzables desde el origen

        # (b) El de menor distancia se vuelve permanente
        #     (desempate: menor número de nodo).
        i = min(temporales, key=lambda n: (u[n], n))
        perm.append(i)

        # (a) Actualizar etiquetas de los sucesores j de i que aún
        #     son temporales; solo se reemplaza si hay mejora.
        mejoras = []
        for (a, j), d in arcos.items():
            if a == i and j not in perm and u[i] + d < u[j]:
                u[j], pred[j] = u[i] + d, i
                mejoras.append(f"u{j}={u[i]}+{d}={u[j]}")
        it += 1
        fila(it)
        print(f"      permanente: nodo {i}  | mejoras: "
              f"{', '.join(mejoras) if mejoras else 'ninguna'}")
    return u, pred


def ruta(pred, t):
    """
    Reconstruye la ruta más corta desde el origen hasta el nodo `t`,
    retrocediendo por los predecesores y luego invirtiendo la lista.
    """
    camino = [t]
    while pred[camino[-1]] not in ("-", None):   # "-" marca el origen
        camino.append(pred[camino[-1]])
    return camino[::-1]


# ---------------------------------------------------------------------
# EJECUCIÓN desde el nodo 1
# ---------------------------------------------------------------------
u, pred = dijkstra(nodos, arcos, s=1)

print("\nDestino | Distancia | Ruta")
for n in nodos[1:]:             # todos los destinos excepto el origen
    print(f"   {n}    |    {u[n]:>3}    | {' -> '.join(map(str, ruta(pred, n)))}")

# ---------------------------------------------------------------------
# VERIFICACIÓN con networkx (distancias desde el nodo 1)
# ---------------------------------------------------------------------
G = nx.DiGraph()                 # grafo dirigido
G.add_weighted_edges_from((i, j, d) for (i, j), d in arcos.items())
print("\nnetworkx:", nx.single_source_dijkstra_path_length(G, 1))
