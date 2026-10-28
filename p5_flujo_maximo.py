"""
=====================================================================
P5. MODELO DE FLUJO MÁXIMO
=====================================================================
Capítulo 6 - Modelos de redes (Investigación Operativa)

PROBLEMA
    Red dirigida con capacidades en los arcos. Fuente s = 1 y
    sumidero t = 6. Determinar el flujo máximo que puede enviarse de s
    a t respetando:
        - Capacidad:    0 <= x_ij <= c_ij en cada arco.
        - Conservación: en cada nodo intermedio, lo que entra es igual
                        a lo que sale.

RED DEL EJERCICIO (capacidades c_ij)
    1->2 = 15   1->3 = 10   1->4 = 12   2->3 = 6    2->5 = 9
    3->5 = 8    3->6 = 7    4->3 = 5    4->6 = 10   5->6 = 14

SE RESUELVE DE TRES FORMAS
    (a) Algoritmo de trayectorias de aumento (red residual).
        - Cada arco tiene capacidad residual (c_ij, c_ji): c_ij es lo
          que aún se puede enviar de i a j, y c_ji lo que se puede
          "devolver" (cancelar) del flujo ya enviado.
        - Se busca una trayectoria s -> t con residual > 0 en todos
          sus arcos. Regla de selección: desde el nodo actual se avanza
          al sucesor con MAYOR residual; si se llega a un callejón sin
          salida, se retrocede.
        - f_p = mínimo residual de la trayectoria (cuello de botella).
          Se actualiza c_ij <- c_ij - f_p  y  c_ji <- c_ji + f_p.
        - Se repite hasta que no existan más trayectorias.
          F = suma de todos los f_p.
    (b) Programación lineal (PuLP):
          max F  s.a. conservación de flujo y 0 <= x_ij <= c_ij.
    (c) Corte mínimo: nodos alcanzables desde s en la red residual
        final = conjunto S; los arcos de S a S̄ forman el corte mínimo.
        Teorema de Ford-Fulkerson: flujo máximo = capacidad del corte
        mínimo.

SALIDA ESPERADA
    F = 31;  corte mínimo S = {1,2,3,4,5}, arcos (3,6),(4,6),(5,6):
    7 + 10 + 14 = 31.
    (El PL puede repartir el flujo distinto: son óptimos alternativos.)

DEPENDENCIAS
    pip install networkx "pulp<4"
"""
import networkx as nx
import pulp

# ---------------------------------------------------------------------
# DATOS: capacidades {(origen, destino): capacidad}
# ---------------------------------------------------------------------
cap = {(1, 2): 15, (1, 3): 10, (1, 4): 12, (2, 3): 6, (2, 5): 9,
       (3, 5): 8, (3, 6): 7, (4, 3): 5, (4, 6): 10, (5, 6): 14}
s, t = 1, 6                                   # fuente y sumidero
nodos = sorted({n for a in cap for n in a})   # lista de nodos

# =====================================================================
# (a) ALGORITMO DE TRAYECTORIAS DE AUMENTO
# =====================================================================
# Red residual r[(i, j)] = capacidad residual del arco i -> j.
# Inicialmente es la capacidad original; el arco inverso (j, i) empieza
# en 0 (setdefault no pisa un valor si ese arco ya existía).
r = {}
for (i, j), c in cap.items():
    r[(i, j)] = r.get((i, j), 0) + c
    r.setdefault((j, i), 0)

F, it = 0, 0          # flujo total acumulado y nº de iteración
print("(a) TRAYECTORIAS DE AUMENTO (mayor capacidad residual)")
while True:
    # ---- Búsqueda de una trayectoria s -> t ----
    camino = [s]          # trayectoria en construcción
    muertos = set()       # nodos sin salida útil (ya descartados)
    while camino and camino[-1] != t:
        i = camino[-1]    # nodo actual (último de la trayectoria)
        # Candidatos: sucesores j con residual > 0 que no estén ya en
        # el camino (evita ciclos) ni descartados. Se guarda
        # (residual, -j, j): max() elige el mayor residual y, en caso
        # de empate, el menor número de nodo.
        cand = [(r[(a, j)], -j, j) for (a, j) in r
                if a == i and r[(a, j)] > 0 and j not in camino
                and j not in muertos]
        if not cand:
            # Callejón sin salida: retroceso (se descarta el nodo).
            muertos.add(camino.pop())
            continue
        camino.append(max(cand)[2])     # avanzar al de mayor residual

    if not camino:
        break             # se retrocedió hasta s: no hay más trayectorias

    # ---- Capacidad de la trayectoria (cuello de botella) ----
    arcos = list(zip(camino[:-1], camino[1:]))   # arcos consecutivos
    f = min(r[a] for a in arcos)                 # f_p = mínimo residual
    it += 1
    print(f"  It. {it}: {'-'.join(map(str, camino))}  "
          f"[{', '.join(f'c{a}{b}={r[(a, b)]}' for a, b in arcos)}] -> f{it} = {f}")

    # ---- Actualización de la red residual ----
    for (i, j) in arcos:
        r[(i, j)] -= f    # se consume capacidad en el sentido directo
        r[(j, i)] += f    # y se habilita devolver flujo en el inverso
    F += f
print(f"  Flujo maximo F = {F}")

# Flujo óptimo en cada arco original = capacidad inicial - residual final.
flujo = {a: cap[a] - r[a] for a in cap}
print("  Flujo por arco:")
for a, c in cap.items():
    print(f"    {a}: {flujo[a]:>2} / {c}")

# =====================================================================
# (c) CORTE MÍNIMO
# Nodos alcanzables desde s con residual > 0 en la red residual final
# (recorrido en profundidad con una pila) forman el lado S del corte.
# =====================================================================
alc, pila = {s}, [s]
while pila:
    i = pila.pop()
    for (a, j), c in r.items():
        if a == i and c > 0 and j not in alc:
            alc.add(j)
            pila.append(j)
# Arcos del corte: salen de S hacia el complemento S̄ (están saturados).
corte = [(i, j) for (i, j) in cap if i in alc and j not in alc]
print(f"\n(c) CORTE MINIMO: S = {sorted(alc)}, S_barra = "
      f"{sorted(set(nodos) - alc)}")
print("    arcos del corte:", corte,
      "| capacidad =", sum(cap[a] for a in corte))

# =====================================================================
# (b) FORMULACIÓN DE PROGRAMACIÓN LINEAL (PuLP)
#   max F
#   s.a. salida - entrada = F   en la fuente
#        entrada - salida = F   en el sumidero
#        entrada - salida = 0   en los nodos intermedios
#        0 <= x_ij <= c_ij
# =====================================================================
m = pulp.LpProblem("Flujo_maximo", pulp.LpMaximize)     # problema de max
# Variable de flujo x_ij por arco, con cota inferior 0 y superior c_ij.
x = {a: pulp.LpVariable(f"x_{a[0]}{a[1]}", 0, c) for a, c in cap.items()}
Fv = pulp.LpVariable("F", lowBound=0)                   # flujo total
m += Fv                                                  # objetivo: max F
for n in nodos:
    sale = pulp.lpSum(x[a] for a in cap if a[0] == n)    # flujo que sale
    entra = pulp.lpSum(x[a] for a in cap if a[1] == n)   # flujo que entra
    if n == s:
        m += (sale - entra == Fv), f"Fuente_{n}"
    elif n == t:
        m += (entra - sale == Fv), f"Sumidero_{n}"
    else:
        m += (entra - sale == 0), f"Nodo_{n}"            # conservación
m.solve(pulp.PULP_CBC_CMD(msg=False))                    # resuelve (CBC)
print("\n(b) PL (PuLP):", pulp.LpStatus[m.status], "| F* =", Fv.value())
for a, v in x.items():
    print(f"    x_{a[0]}{a[1]} = {v.value():>4.0f}  (c = {cap[a]})")

# =====================================================================
# VERIFICACIÓN con networkx (flujo máximo y corte mínimo)
# =====================================================================
G = nx.DiGraph()
for (i, j), c in cap.items():
    G.add_edge(i, j, capacity=c)          # atributo "capacity"
val, _ = nx.maximum_flow(G, s, t)         # valor del flujo máximo
print("\nnetworkx: flujo maximo =", val, "| corte minimo =",
      nx.minimum_cut(G, s, t)[0])         # [0] = valor del corte mínimo
