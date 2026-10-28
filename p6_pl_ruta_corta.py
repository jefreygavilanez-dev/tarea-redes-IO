"""
=====================================================================
P6. FORMULACIÓN DE PL DE LA RUTA MÁS CORTA (primal, dual y holgura)
=====================================================================
Capítulo 6 - Modelos de redes (Investigación Operativa)

PROBLEMA
    Escribir y resolver el modelo primal y el dual del problema P2
    (red dirigida) para ir del nodo s = 1 al nodo t = 6, y verificar
    la holgura complementaria.

RED (la misma de P2)
    1->2 = 5    1->3 = 2    3->2 = 1    2->4 = 4    2->5 = 9
    3->4 = 8    3->5 = 12   4->5 = 3    4->6 = 7    5->6 = 2

MODELO PRIMAL (se envía 1 unidad de flujo de s a t)
    x_ij = 1 si el arco (i,j) está en la ruta, 0 si no.
        min z = sum_{(i,j)} d_ij * x_ij
        s.a.  (flujo que sale) - (flujo que entra) =
                  +1   si i = s  (origen)
                   0   si i != s, t  (transbordo)
                  -1   si i = t  (destino)
              x_ij >= 0
    La matriz de restricciones es totalmente unimodular, por lo que
    el simplex da solución entera (0 ó 1) sin imponer binarias.

MODELO DUAL (una variable libre u_i por cada restricción de nodo)
        max w = u_t - u_s
        s.a.  u_j - u_i <= d_ij   para todo arco (i,j)
              u_s = 0,   u_i libres
    u_j se interpreta como la distancia desde el origen hasta j.

HOLGURA COMPLEMENTARIA
    En el óptimo, para todo arco:  x_ij * (d_ij - (u_j - u_i)) = 0
    Es decir: si el arco está en la ruta (x_ij = 1), su restricción
    dual es una igualdad (u_j - u_i = d_ij); si la restricción dual
    tiene holgura positiva, entonces x_ij = 0.

SALIDA ESPERADA
    z* = w* = 12;  u = (0, 3, 2, 7, 10, 12);  ruta 1-3-2-4-5-6

DEPENDENCIAS
    pip install "pulp<4"
"""
import pulp

# ---------------------------------------------------------------------
# DATOS: longitudes {(origen, destino): d_ij}
# ---------------------------------------------------------------------
arcos = {(1, 2): 5, (1, 3): 2, (3, 2): 1, (2, 4): 4, (2, 5): 9,
         (3, 4): 8, (3, 5): 12, (4, 5): 3, (4, 6): 7, (5, 6): 2}
nodos = sorted({n for a in arcos for n in a})
s, t = 1, 6                          # origen y destino

# =====================================================================
# MODELO PRIMAL
# =====================================================================
primal = pulp.LpProblem("Ruta_mas_corta", pulp.LpMinimize)

# Una variable x_ij >= 0 por arco (cantidad de flujo por ese arco).
x = {a: pulp.LpVariable(f"x_{a[0]}{a[1]}", lowBound=0) for a in arcos}

# Función objetivo: minimizar la longitud total  sum d_ij * x_ij.
primal += pulp.lpSum(d * x[a] for a, d in arcos.items())

# Una restricción de balance de flujo por cada nodo.
for n in nodos:
    sale = pulp.lpSum(x[a] for a in arcos if a[0] == n)     # arcos que salen
    entra = pulp.lpSum(x[a] for a in arcos if a[1] == n)    # arcos que entran
    # Oferta neta: +1 en el origen, -1 en el destino, 0 en transbordos.
    oferta = 1 if n == s else (-1 if n == t else 0)
    primal += (sale - entra == oferta), f"Nodo_{n}"

primal.solve(pulp.PULP_CBC_CMD(msg=False))

print("PRIMAL:", pulp.LpStatus[primal.status], "| z* =", pulp.value(primal.objective))
for a, v in x.items():
    if v.value() > 1e-9:             # solo los arcos que usa la ruta
        print(f"  x_{a[0]}{a[1]} = {v.value():.0f}  (d = {arcos[a]})")

# =====================================================================
# MODELO DUAL
# =====================================================================
dual = pulp.LpProblem("Dual_ruta_mas_corta", pulp.LpMaximize)

# Variables duales u_i SIN restricción de signo (libres): por eso no
# se les da cota inferior.
u = {n: pulp.LpVariable(f"u_{n}") for n in nodos}

# Objetivo: maximizar u_t - u_s (distancia del origen al destino).
dual += u[t] - u[s]

# Una restricción por cada arco: u_j - u_i <= d_ij.
for (i, j), d in arcos.items():
    dual += (u[j] - u[i] <= d), f"Arco_{i}{j}"

# Referencia: la distancia del origen a sí mismo es 0.
dual += (u[s] == 0)
dual.solve(pulp.PULP_CBC_CMD(msg=False))

print("\nDUAL:", pulp.LpStatus[dual.status], "| w* =", pulp.value(dual.objective))
print("  u =", {k: v.value() for k, v in u.items()})

# =====================================================================
# VERIFICACIÓN DE LA HOLGURA COMPLEMENTARIA
#   x_ij * (d_ij - (u_j - u_i)) = 0   para todo arco (i,j)
# "holgura" = d_ij - (u_j - u_i) >= 0 (por factibilidad dual).
# =====================================================================
print("\nHOLGURA COMPLEMENTARIA:  x_ij * (d_ij - (u_j - u_i)) = 0")
print(f"{'arco':<7}{'x_ij':>5}{'u_j-u_i':>9}{'d_ij':>6}{'holgura':>9}  cumple")
ok = True                            # se vuelve False si algún arco falla
for (i, j), d in arcos.items():
    xv = x[(i, j)].value()                       # flujo primal del arco
    hol = d - (u[j].value() - u[i].value())      # holgura de la restr. dual
    # Producto ~ 0 (con tolerancia numérica): x_ij = 0 o holgura = 0.
    cumple = abs(xv * hol) < 1e-9
    ok &= cumple
    print(f"({i},{j})  {xv:>5.0f}{u[j].value()-u[i].value():>9.0f}{d:>6}{hol:>9.0f}  "
          f"{'si' if cumple else 'NO'}")

print("\nTodas las condiciones se cumplen:", ok)
# Dualidad fuerte: los valores óptimos primal y dual deben coincidir.
print("z* = w* ?", abs(pulp.value(primal.objective) - pulp.value(dual.objective)) < 1e-9)
