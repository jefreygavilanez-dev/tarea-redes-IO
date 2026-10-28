"""
=====================================================================
P1. ÁRBOL DE MÍNIMA EXPANSIÓN (AME)
=====================================================================
Capítulo 6 - Modelos de redes (Investigación Operativa)

PROBLEMA
    Dada una red NO dirigida con longitudes en las aristas, conectar
    todos los nodos usando el conjunto de aristas de longitud total
    mínima. La solución es un árbol de expansión: conecta los n nodos
    con exactamente n - 1 aristas y no contiene ciclos.

RED DEL EJERCICIO (7 nodos, 12 aristas)
    (1,2)=4  (1,3)=6  (1,4)=5  (2,3)=3  (2,5)=7  (3,4)=4
    (3,5)=5  (3,6)=6  (4,6)=8  (5,6)=2  (5,7)=6  (6,7)=3

MÉTODOS IMPLEMENTADOS
    1) Algoritmo de Prim (método del texto de Taha):
         - C  = conjunto de nodos ya conectados.
         - C̄  = conjunto de nodos aún sin conectar.
         - En cada iteración se elige, entre todas las aristas que
           unen un nodo de C con un nodo de C̄, la más corta, y su
           extremo pasa de C̄ a C. Termina cuando C̄ queda vacío.
    2) Algoritmo de Kruskal (comprobación):
         - Ordena las aristas de menor a mayor longitud.
         - Acepta una arista solo si NO forma ciclo con las ya
           aceptadas (se detecta con la estructura "unión-búsqueda").
         - Termina al aceptar n - 1 aristas.
    3) Verificación con la librería networkx.

SALIDA ESPERADA
    AME = {(1,2), (2,3), (3,4), (3,5), (5,6), (6,7)},  L = 21

DEPENDENCIAS
    pip install networkx
"""
import networkx as nx

# ---------------------------------------------------------------------
# DATOS DE LA RED
# Cada arista se escribe como (nodo_i, nodo_j, longitud).
# Como la red es no dirigida, (i, j) y (j, i) son la misma arista.
# ---------------------------------------------------------------------
aristas = [(1, 2, 4), (1, 3, 6), (1, 4, 5), (2, 3, 3), (2, 5, 7),
           (3, 4, 4), (3, 5, 5), (3, 6, 6), (4, 6, 8), (5, 6, 2),
           (5, 7, 6), (6, 7, 3)]

# Lista ordenada de nodos, deducida de los extremos de las aristas
# (un conjunto elimina repetidos y sorted() los ordena).
nodos = sorted({n for i, j, _ in aristas for n in (i, j)})


def prim(nodos, aristas, inicio=1):
    """
    Algoritmo de Prim: hace crecer UN solo árbol desde el nodo `inicio`.

    Parámetros
    ----------
    nodos   : lista con todos los nodos de la red.
    aristas : lista de tuplas (i, j, longitud).
    inicio  : nodo desde el cual se empieza a construir el árbol.

    Retorna
    -------
    (arbol, total)
        arbol : lista de aristas (i, j, longitud) elegidas, en el
                orden en que Prim las fue agregando.
        total : longitud total del árbol.
    """
    # Lista de adyacencia: adj[i][j] = longitud de la arista {i, j}.
    # Se guarda en ambos sentidos porque la red es no dirigida.
    adj = {n: {} for n in nodos}
    for i, j, w in aristas:
        adj[i][j] = w
        adj[j][i] = w

    C = {inicio}                    # nodos ya conectados (C)
    Cb = set(nodos) - C             # nodos aún sin conectar (C barra)
    arbol, total, k = [], 0, 0      # resultado, longitud y nº iteración
    print(f"It. {k}: C = {sorted(C)}")

    # Se repite hasta conectar todos los nodos (C barra vacío).
    while Cb:
        k += 1
        # Aristas candidatas: unen un nodo i de C con un nodo j de C̄.
        # Se guardan como (longitud, i, j) para poder ordenarlas por
        # longitud; ante empates se desempata por menor índice.
        cand = sorted((adj[i][j], i, j)
                      for i in C for j in adj[i] if j in Cb)
        txt = ", ".join(f"({i},{j})={w}" for w, i, j in cand)

        # La arista más corta es la primera de la lista ordenada.
        w, i, j = cand[0]

        # El nodo j se incorpora al conjunto de nodos conectados.
        C.add(j)
        Cb.remove(j)
        arbol.append((i, j, w))
        total += w
        print(f"It. {k}: candidatas {txt}\n        elegida ({i},{j}) = {w}")
    return arbol, total


def kruskal(nodos, aristas):
    """
    Algoritmo de Kruskal: recorre las aristas de menor a mayor
    longitud y acepta cada una si NO cierra un ciclo.

    Para detectar ciclos se usa "unión-búsqueda" (union-find): cada
    nodo apunta a un representante de su componente conexa; dos nodos
    con el mismo representante ya están conectados, y unirlos
    cerraría un ciclo.

    Retorna
    -------
    (arbol, total) con el mismo formato que `prim`.
    """
    # Inicialmente cada nodo es su propia componente (su propio padre).
    padre = {n: n for n in nodos}

    def raiz(x):
        """Busca el representante (raíz) de la componente de x."""
        while padre[x] != x:
            x = padre[x]
        return x

    arbol, total = [], 0
    # Orden de procesamiento: por longitud, luego por nodos (empates).
    for i, j, w in sorted(aristas, key=lambda a: (a[2], a[0], a[1])):
        ri, rj = raiz(i), raiz(j)
        if ri != rj:
            # Componentes distintas: la arista NO forma ciclo -> se
            # acepta y se fusionan las dos componentes.
            padre[rj] = ri
            arbol.append((i, j, w))
            total += w
            estado = "ACEPTADA"
        else:
            # Mismas componentes: aceptar la arista cerraría un ciclo.
            estado = "rechazada (forma ciclo)"
        print(f"  arista ({i},{j}) = {w}: {estado}")

        # Un árbol de expansión tiene n - 1 aristas: ya terminó.
        if len(arbol) == len(nodos) - 1:
            break
    return arbol, total


# ---------------------------------------------------------------------
# EJECUCIÓN: Prim y Kruskal deben dar la misma longitud total
# ---------------------------------------------------------------------
print("=== PRIM (inicio en el nodo 1) ===")
ame_p, L_p = prim(nodos, aristas)
print("AME (Prim):", [(i, j) for i, j, _ in ame_p], "| L =", L_p)

print("\n=== KRUSKAL ===")
ame_k, L_k = kruskal(nodos, aristas)
print("AME (Kruskal):", [(i, j) for i, j, _ in ame_k], "| L =", L_k)

# ---------------------------------------------------------------------
# VERIFICACIÓN con networkx (implementación de referencia)
# ---------------------------------------------------------------------
G = nx.Graph()                       # grafo no dirigido
G.add_weighted_edges_from(aristas)   # aristas con atributo "weight"
T = nx.minimum_spanning_tree(G)      # árbol de mínima expansión
print("\nnetworkx: L =", T.size(weight="weight"),
      "| aristas =", sorted(tuple(sorted(e)) for e in T.edges()))
