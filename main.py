# General librairies
from methods import Pso, De, Abc
import matplotlib.pyplot as plt
import numpy as np
import os
import shutil

# Usecase librairies
import math
from matplotlib.patches import Polygon as MatplotlibPolygon
import matplotlib.animation as animation
from shapely.geometry import Polygon
from shapely import intersects,intersection,normalize

def empty_directory(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            os.remove(file_path)

        for dir in dirs:
            dir_path = os.path.join(root, dir)
            shutil.rmtree(dir_path)

empty_directory("KPI/PSO")
empty_directory("KPI/DE")
empty_directory("KPI/ABC")

def plot_optimization_progress(params, optimizer, optimizer_instance):
    
    num_runs = 30
    best_fitness_data = [] 
    best_position_progress_data = []
    best_fitness_progress_data = []
    for run in range(num_runs):
        if optimizer == 'PSO':
            _, best_fitness, best_position_progress_run , best_fitness_progress_run = optimizer_instance.pso(params)
        elif optimizer == 'DE':
            _, best_fitness, best_position_progress_run , best_fitness_progress_run = optimizer_instance.de(params)
        elif optimizer == 'ABC':
            _, best_fitness, best_position_progress_run , best_fitness_progress_run = optimizer_instance.abc(params)

        best_fitness_data.append(best_fitness) 
        best_position_progress_data.append(best_position_progress_run) 
        best_fitness_progress_data.append(best_fitness_progress_run)
    
    if optimizer == 'PSO':
        num_iterations = list(range(1, params.num_cycles + 1))
    elif optimizer == 'DE':
        num_iterations = list(range(1, params.max_generations + 1))
    elif optimizer == 'ABC':
        num_iterations = list(range(1, params.max_trials + 1))

    best_fitness_index = np.argmax(best_fitness_data)
    best_position_progress = best_position_progress_data[best_fitness_index]
    best_fitness_progress = best_fitness_progress_data[best_fitness_index]

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.axis('equal')
    ax.set_title(f'{optimizer} - Animation')
    
    def init():
        pass

    def draw(position, poly):
        x, y = position[0], position[1]  # Point d'ancrage du rectangle
        w = position[2]  # Largeur
        h = position[3]  # Hauteur
        angle = position[4]  # Angle (en degrés)

        theta = math.radians(angle)

        corners = [(x, y)] 
        for i in range(3):
            if i == 1:
                d = w  
            else:
                d = h  

            # Calculez les coordonnées du prochain coin en fonction de l'angle et de la distance
            tmp_x = corners[-1][0] + d * math.cos(theta)
            tmp_y = corners[-1][1] + d * math.sin(theta)

            corners.append((tmp_x, tmp_y))

            # Ajoutez 90 degrés à l'angle pour le prochain coin
            theta += math.radians(90)

        rect_polygon = MatplotlibPolygon(corners, fill=True, color="red", alpha=1)    
        poly_polygon = MatplotlibPolygon(poly, fill=True, alpha=0.2)
        ax.add_patch(rect_polygon)
        ax.add_patch(poly_polygon)
        ax.autoscale_view()

    def update_draw(frame):
        ax.clear()
        ax.axis('equal')
        ax.axis('off')
        ax.set_title(f'{optimizer} - Best Run ')
        draw(best_position_progress[frame], poly)
        ax_fitness = ax.inset_axes([0, 0, 0.2, 0.2])
        ax_fitness.plot(num_iterations[:frame+1], best_fitness_progress[:frame+1])
        ax_fitness.set_xlabel('Iteration')
        ax_fitness.set_ylabel('Fitness')

    ani = animation.FuncAnimation(fig, update_draw, frames=len(best_position_progress), init_func=init, repeat=False, blit=False)
    ani.save(f'Animation/{optimizer}/{str(optimizer).lower()}_best_run_animation.gif', writer='pillow', fps=10)  

    # Crée un graphique en affichant les meilleures fitness en y et les runs en x
    plt.figure()
    plt.plot(list(range(1, num_runs + 1)), best_fitness_data)
    plt.title(f"{optimizer} - Best Fitness across Runs")
    plt.xlabel("Run")
    plt.ylabel("Best Fitness")
    plt.grid()
    plt.savefig(f'KPI/{optimizer}/{str(optimizer).lower()}_progress_across_runs.png')  # Sauvegarde le graphique dans un dossier "kpi"

    # Génère un fichier texte avec les informations
    with open(f'KPI/{optimizer}/{str(optimizer).lower()}_parameters_statistics.txt', 'w') as f:
        f.write(f"#--------------------#\n")

        f.write(f"\n{optimizer} - Parameters\n\n")
        param_dict = {key: getattr(params, key) for key in dir(params) if not key.startswith("__")}
        for param, value in param_dict.items():
            f.write(f"{param}: {value}\n")

        f.write(f"\n#--------------------#\n")

        f.write(f"\n{optimizer} - Statistics:\n\n")
        f.write(f"Runs: {num_runs}\n")
        f.write(f"Mean Best Fitness: {np.mean(best_fitness_data)}\n")
        f.write(f"Median Best Fitness: {np.median(best_fitness_data)}\n")
        f.write(f"Standard Deviation: {np.std(best_fitness_data)}\n")
        f.write(f"Minimum Best Fitness: {np.min(best_fitness_data)}\n")
        f.write(f"Maximum Best Fitness: {np.max(best_fitness_data)}\n")

        f.write(f"\n#--------------------#n")

if __name__ == "__main__":
    # UseCase : find the rectangle with the largest area that fits a polygon
    INF = -500
    SUP = 500 
    MIN_ANGLE = 0 
    MAX_ANGLE = 360
    poly = ((50, 150), (200, 50), (350, 150), (350, 300), (250, 300), (200, 250), (150, 350), (100, 250), (100, 200))

    # Global parameters
    bounds = []
    for _ in range (4):
        bounds.append((INF,SUP))
    bounds.append((MIN_ANGLE,MAX_ANGLE))
    num_dimensions = 5

    # Parameters for PSO
    num_particles = 30
    num_cycles = 100
    psi = 0.5 
    c1 = 1.5  
    c2 = 1.5 

    # Parameters for DE
    num_population = 30
    scaling_factor = 0.5 
    crossover_rate = 0.7  
    max_generations = 100  

    # Parameters for ABC
    num_employed_bees = 30
    num_onlooker_bees = 30
    num_scout_bees = 30
    max_trials = 50

    # Instance of class 
    pso_optimizer = Pso()
    de_optimizer = De()
    abc_optimizer = Abc()

    # Objective function (adapted to the usecase)
    def objective_function(position):
        poly = ((50, 150), (200, 50), (350, 150), (350, 300), (250, 300), (200, 250), (150, 350), (100, 250), (100, 200))

        x, y = position[0], position[1]  # Point d'ancrage du rectangle
        w = position[2]  # Largeur
        h = position[3]  # Hauteur
        angle = position[4]  # Angle (en degrés)

        # Conversion de l'angle en radians
        theta = math.radians(angle)

        corners = [(x, y)]  # Ajoutez le point d'ancrage comme premier coin

        for i in range(3):
            if i == 1:
                d = w  # Utilisez la largeur pour le deuxième coin
            else:
                d = h  # Utilisez la hauteur pour les deux derniers coins

            # Calculez les coordonnées du prochain coin en fonction de l'angle et de la distance
            tmp_x = corners[-1][0] + d * math.cos(theta)
            tmp_y = corners[-1][1] + d * math.sin(theta)

            corners.append((tmp_x, tmp_y))

            # Ajoutez 90 degrés à l'angle pour le prochain coin
            theta += math.radians(90)
        
        # Créez un Polygon à partir des coins du rectangle
        r = Polygon(corners)

        # Créez un Polygon à partir des coordonnées du polygon
        p = Polygon(poly)

        if p.contains(r):
            res_area = r.area
            # print(f"Aire rectangle (contains) = {res_area}")
        elif p.intersects(r):
            intersection_area = p.intersection(r).area
            total_area = r.area
            outside_area = total_area - intersection_area
            res_area = 0 - outside_area
            # print(f"Aire rectangle (inter) = {res_area}")
        else:
            res_area = -10000
            # print(f"Aire rectangle (out) = {res_area}")

        return res_area

    # Instance of Parameters
    pso_params = pso_optimizer.Parameters(objective_function, bounds, num_dimensions, num_particles, num_cycles, psi, c1, c2)
    de_params = de_optimizer.Parameters(objective_function, bounds, num_dimensions, num_population, scaling_factor, crossover_rate, max_generations)
    abc_params = abc_optimizer.Parameters(objective_function, bounds, num_dimensions, num_employed_bees, num_onlooker_bees, num_scout_bees, max_trials)

    # Running and redering optimization
    plot_optimization_progress(pso_params, 'PSO', pso_optimizer)
    plot_optimization_progress(de_params, 'DE', de_optimizer)
    plot_optimization_progress(abc_params, 'ABC', abc_optimizer)

   