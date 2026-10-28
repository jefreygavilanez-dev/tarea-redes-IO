"""
=====================================================================
P3. ALGORITMO DE FLOYD (rutas más cortas entre TODOS los pares)
=====================================================================
Capítulo 6 - Modelos de redes (Investigación Operativa)

PROBLEMA
    Red NO dirigida de 4 nodos con las aristas:
        (1,2)=5   (1,3)=3   (2,3)=1   (2,4)=8   (3,4)=9
    Obtener las matrices D4 y S4 y la ruta más corta de 1 a 4.

MATRICES
    D : matriz de distancias. D0[i][j] = longitud del arco (i,j);
        infinito si no hay arco directo; diagonal = 0 (no se usa).
    S : matriz de secuencia. S0[i][j] = j (se va directo de i a j).
        Cuando se mejora una ruta pasando por k, se anota s_ij = k.

OPERACIÓN TRIPLE
    Dados tres nodos i, j, k: conviene pasar por k para ir de i a j si
        d_ik + d_kj < d_ij
    y en ese caso:  d_ij <- d_ik + d_kj   y   s_ij <- k.

ALGORITMO
    Para k = 1, ..., n (nodo pivote): se aplica la operación triple a
    todos los d_ij que NO estén en la fila k ni en la columna k ni en
    la diagonal. Al final, D contiene las distancias mínimas.

LECTURA DE RUTAS
    Si s_ij = j el arco es directo. Si s_ij = k != j la ruta es
    i -> ... -> k -> ... -> j y se repite el análisis con s_ik y s_kj.

SALIDA ESPERADA
    d14 = 12, ruta 1-3-4 (empate con 1-3-2-4, que también suma 12).

DEPENDENCIAS
    pip install numpy networkx
"""
import numpy as np
import networkx as nx

INF = np.inf        # "infinito": no existe arco directo
n = 4               # número de nodos

# Aristas (i, j, distancia) de la red no dirigida.
aristas = [(1, 2, 5), (1, 3, 3), (2, 3, 1), (2, 4, 8), (3, 4, 9)]

# ---------------------------------------------------------------------
# MATRICES INICIALES D0 y S0
# ---------------------------------------------------------------------
D = np.full((n, n), INF)        # todo infinito...
np.fill_diagonal(D, 0)          # ...y diagonal en 0 (distancia a sí mismo)
for i, j, d in aristas:
    # Red no dirigida: la arista se carga en ambos sentidos.
    # (Los nodos se numeran desde 1 pero los índices de numpy desde 0.)
    D[i - 1, j - 1] = d
    D[j - 1, i - 1] = d

# S0: cada fila es [1, 2, ..., n]  ->  s_ij = j (ir directo).
S = np.tile(np.arange(1, n + 1), (n, 1))


def mostrar(D, S, k):
    """Imprime lado a lado las matrices D_k y S_k de la iteración k."""
    print(f"--- D{k} ---" + " " * 24 + f"--- S{k} ---")
    for i in range(n):
        fd = " ".join(f"{'inf' if x == INF else int(x):>4}" for x in D[i])
        fs = " ".join(f"{x:>3}" for x in S[i])
        print(f"{fd}      {fs}")


# ---------------------------------------------------------------------
# ITERACIONES DE FLOYD
# ---------------------------------------------------------------------
mostrar(D, S, 0)
for k in range(n):                      # k+1 es el nodo pivote
    for i in range(n):
        for j in range(n):
            # Se ignoran fila k, columna k y diagonal; se aplica la
            # operación triple solo si la ruta por k es estrictamente
            # más corta que la actual.
            if i != k and j != k and i != j and D[i, k] + D[k, j] < D[i, j]:
                print(f"k={k+1}: d{i+1}{j+1} = d{i+1}{k+1} + d{k+1}{j+1} = "
                      f"{int(D[i,k])}+{int(D[k,j])} = {int(D[i,k]+D[k,j])}"
                      f" < {'inf' if D[i,j]==INF else int(D[i,j])}")
                D[i, j] = D[i, k] + D[k, j]     # nueva distancia
                S[i, j] = k + 1                 # k es nodo intermedio
    mostrar(D, S, k + 1)                # matrices D_k y S_k


def ruta(S, i, j):
    """
    Reconstruye de forma recursiva la ruta más corta i -> j usando S.
        - Si s_ij = j: el arco (i, j) es directo.
        - Si no: pasa por k = s_ij, y se une la ruta i->k con la k->j
          (se omite el primer nodo de la segunda para no repetir k).
    """
    k = int(S[i - 1, j - 1])
    if k == j:
        return [i, j]
    return ruta(S, i, k) + ruta(S, k, j)[1:]


# ---------------------------------------------------------------------
# RESULTADO: ruta 1 -> 4
# ---------------------------------------------------------------------
r = ruta(S, 1, 4)
print("\nRuta 1 -> 4:", " -> ".join(map(str, r)), "| distancia =", int(D[0, 3]))

# ---------------------------------------------------------------------
# VERIFICACIÓN con networkx
# ---------------------------------------------------------------------
G = nx.Graph()
G.add_weighted_edges_from(aristas)
# Distancia 1->4 y TODAS las rutas mínimas (muestra el empate).
print("networkx 1->4:", nx.dijkstra_path_length(G, 1, 4),
      "| todas las rutas minimas:",
      list(nx.all_shortest_paths(G, 1, 4, weight="weight")))
# La matriz D final debe coincidir con la de Floyd-Warshall de networkx.
print("Coincide con networkx:",
      np.array_equal(D, nx.floyd_warshall_numpy(G, nodelist=range(1, n + 1))))
