"""
=====================================================================
P4. REEMPLAZO DE EQUIPO (modelado como ruta más corta)
=====================================================================
Capítulo 6 - Modelos de redes (Investigación Operativa)

PROBLEMA
    Una máquina cuesta $30 000 (30 miles de USD). Datos por año de uso:
        Año de uso t          :   1    2    3    4    5
        Mantenimiento (miles) :   3    4    6    9   13
        Reventa tras t años   :  22   17   13   10    7
    Horizonte de 5 años (nodos 1 a 6). Determinar la política óptima
    de reemplazo que minimiza el costo total.

MODELO DE RED
    - Nodo i = inicio del año i (i = 1, ..., 6).
    - Arco (i, j) = "comprar una máquina al inicio del año i y
      venderla al inicio del año j" (se conserva t = j - i años).
    - Costo del arco:
          c_ij = c(t) = precio + sum_{k=1..t} mantenimiento_k - reventa_t
    - La política óptima es la RUTA MÁS CORTA del nodo 1 al nodo 6.

MÉTODO
    La red es acíclica (todos los arcos van de un nodo menor a uno
    mayor), así que se resuelve con programación hacia adelante:
        u_1 = 0,    u_j = min_{i<j} { u_i + c(j - i) }
    Después se verifica con Dijkstra de networkx, que además enumera
    TODAS las políticas óptimas (hay un empate).

SALIDA ESPERADA
    c(t) = 11, 20, 30, 42, 58;  costo mínimo = 50 mil USD
    políticas óptimas: 1->3->6  y  1->4->6

DEPENDENCIAS
    pip install networkx
"""
import networkx as nx

# ---------------------------------------------------------------------
# DATOS DEL PROBLEMA
# ---------------------------------------------------------------------
precio = 30                       # precio de una máquina nueva (miles USD)
mant = [3, 4, 6, 9, 13]           # mantenimiento en el año 1..5 de uso
reventa = [22, 17, 13, 10, 7]     # valor de reventa tras 1..5 años de uso
N = 5                             # años del horizonte (nodos 1..N+1)


def costo(t):
    """
    Costo neto de comprar una máquina y conservarla t años:
        precio + (mantenimientos de los años 1..t) - reventa tras t años.
    `mant[:t]` toma los primeros t mantenimientos; `reventa[t-1]` es la
    reventa tras t años (las listas empiezan en índice 0).
    """
    return precio + sum(mant[:t]) - reventa[t - 1]


# ---------------------------------------------------------------------
# PASO 1-2: TABLA DE COSTOS c(t)
# ---------------------------------------------------------------------
print("Costos c(t):")
for t in range(1, N + 1):
    print(f"  c({t}) = {precio} + {sum(mant[:t])} - {reventa[t-1]} = {costo(t)}")

# ---------------------------------------------------------------------
# CONSTRUCCIÓN DE LA RED (para la verificación con networkx)
# Un arco (i, j) por cada par i < j; su costo solo depende de t = j - i.
# ---------------------------------------------------------------------
R = nx.DiGraph()
for i in range(1, N + 1):
    for j in range(i + 1, N + 2):
        R.add_edge(i, j, weight=costo(j - i))

# ---------------------------------------------------------------------
# PASO 3: PROGRAMACIÓN HACIA ADELANTE
# u[j] = costo mínimo de tener máquina funcionando hasta el inicio del
# año j. Se calcula en orden creciente de j porque la red es acíclica.
# ---------------------------------------------------------------------
u = {1: 0}                        # estamos en el inicio del año 1 sin costo
origen = {}                       # nodos desde los que se logra el mínimo
print("\nDistancias minimas:")
for j in range(2, N + 2):
    # Opciones para llegar a j: venir desde cada i < j pagando c(j - i).
    opciones = {i: u[i] + costo(j - i) for i in range(1, j)}
    u[j] = min(opciones.values())
    # Todos los i que alcanzan el mínimo (si hay más de uno: empate).
    origen[j] = [i for i, v in opciones.items() if v == u[j]]
    print(f"  u{j} = min{list(opciones.values())} = {u[j]}  (desde {origen[j]})")

# ---------------------------------------------------------------------
# RESULTADO: todas las políticas óptimas y su costo
# ---------------------------------------------------------------------
print("\nPoliticas optimas (todas):")
for p in nx.all_shortest_paths(R, 1, N + 1, weight="weight"):
    print("  ", " -> ".join(map(str, p)))
print(f"Costo minimo = {nx.dijkstra_path_length(R, 1, N + 1)} mil USD "
      f"(${nx.dijkstra_path_length(R, 1, N + 1) * 1000:,.0f})")
