from typing import List
import igraph as ig


def kempe_neighbourhood(self: ig.Graph):
    """
    Retorna la vecindad de Kempe de una coloración.

    Esto lo hace obteniendo todos los posibles intercabios de kempe.
    """
    # Obtener la coloración actual
    coloring = self.coloring_as_dict()

    # Inicializar la vecindad de Kempe
    kempe = []

    # Obetener los colores utilizados en la coloración
    colors = {v['color'] for v in self.vs if v['color'] and v['color'] != ''}

    # Construir conjunto de pares no-ordenados de colores
    pairs = [(c1, c2) for c1 in colors for c2 in colors if c1 < c2]

    # Iterar sobre los pares de colores
    for c1, c2 in pairs:
        # Hallar los ids nodos que tienen los colores c1 y c2
        pair_set = {c1, c2}
        nodes = [v.index for v in self.vs if v['color']
                 == c1 or v['color'] == c2]

        # Halla el subgrafo inducido por los nodos
        subgraph = self.induced_subgraph(
            nodes, implementation="copy_and_delete")

        # Obtener las componentes conexas
        components = subgraph.connected_components()

        # Iterar sobre las componentes conexas
        for component in components:
            # Si la componente tiene un solo nodo, no se puede intercambiar
            if len(component) == 1:
                continue

            # Copiar la coloración actual
            new_coloring = coloring.copy()

            # Por cada nodo en la componente
            for nc in component:
                # Hallar el indice en el grafo original
                node = nodes[nc]

                # Hallar el color actual del nodo
                current_color = coloring[node]

                # Intercambiar los colores
                new_color = c1 if current_color == c2 else c2

                # Actualizar la coloración con el nuevo color
                new_coloring[node] = new_color

            # Agregar la nueva coloración a la vecindad de Kempe
            kempe.append(new_coloring)

    return kempe


def eval_sum_of_squared_color_sizes(coloring: dict[int, str]):
    """
    Evalúa una coloración de un grafo sumando el cuadrado de la 
    cantidad de nodos que tienen cada color.

    Si se maximiza esta función, implica que se minimiza la cantidad de colores.
    """
    # Obtener los colores utilizados en la coloración (a partir de coloring)
    colors = {color for color in coloring.values()}

    # Inicializar la suma de cuadrados de tamaños de colores
    sum_of_squared_color_sizes = 0

    # Iterar sobre los colores
    for color in colors:
        # Hallar los nodos que tienen el color actual
        nodes = [node for node, c in coloring.items() if c == color]

        # Calcular el cuadrado de la cantidad de nodos
        squared_size = len(nodes) ** 2

        # Sumar el cuadrado al total
        sum_of_squared_color_sizes += squared_size

    return sum_of_squared_color_sizes


def kempe_sorted(self: ig.Graph):
    """
    Retorna la vecindad de Kempe de una coloración ordenada por evaluación.

    Adicionalmente, retorna el primer vecino de la vecindad ordenada 
    y su evaluación.
    """

    neighbours = self.kempe_neighbourhood()
    evals = [eval_sum_of_squared_color_sizes(v) for v in neighbours]

    # Ordenar los vecinos por evaluación de mayor a menor
    neighbours, evals = zip(
        *sorted(zip(neighbours, evals), key=lambda x: -x[1]))

    # Obtener el mejor vecino
    best = neighbours[0] if len(neighbours) > 0 else None
    best_eval = evals[0] if len(evals) > 0 else None

    return neighbours, best, best_eval


def local_search(self: ig.Graph):
    """
    Coloración local del grafo utilizando busqueda local con la vecindad de Kempe.
    """
    # Al maximizar esta función, se minimiza la cantidad de colores
    eval_sol = eval_sum_of_squared_color_sizes

    # Nuestra solución inicial será la salida de D-Satur
    self.d_satur()

    # Obtenemos la vecindad de Kempe ordenada por evaluación
    _, best, best_eval = self.kempe_sorted()

    # Mientras la evaluación de la mejor solución vecina sea mejor que la actual
    while best is not None and best_eval > eval_sol(self.coloring_as_dict()):
        # Aplicamos el mejor vecino
        self.apply_coloring_dict(best)

        # Obtenemos la vecindad de Kempe ordenada por evaluación
        _, best, best_eval = self.kempe_sorted()
