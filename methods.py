import random
import copy

# region 1 : PSO
class Pso:
    class Parameters:
        def __init__(self, objective_function, bounds, num_dimensions, num_particles, num_cycles, psi, c1, c2):
            self.objective_function = objective_function
            self.bounds = bounds  # 2D
            self.num_dimensions = num_dimensions
            self.num_particles = num_particles
            self.num_cycles = num_cycles
            self.psi = psi
            self.c1 = c1
            self.c2 = c2

    class Particle:
        def __init__(self, position, fitness, personal_best_position, personal_best_fitness, informants_best_position,
                    informants_best_fitness, velocity):
            self.position = position
            self.fitness = fitness
            self.personal_best_position = personal_best_position
            self.personal_best_fitness = personal_best_fitness
            self.informants_best_position = informants_best_position
            self.informants_best_fitness = informants_best_fitness
            self.velocity = velocity

    def controled_particles(self, particles, params):
        sublist_particles = []
        for particle in particles : 
            take = True
            for i,position in enumerate(particle.position) : 
                if params.bounds[i][0] > position or position > params.bounds[i][1] : 
                    take = False
            if take : 
                sublist_particles.append(particle)
        return sublist_particles
    
    def init_particles(self, params):
        particles = []
        for _ in range(params.num_particles):
            positions = []
            for bound in params.bounds : 
                position = random.uniform(bound[0],bound[1])
                positions.append(position)
            new_particle = self.Particle(positions, params.objective_function(positions), positions,
                                        params.objective_function(positions), None, None, [0.0] * params.num_dimensions)
            particles.append(new_particle)
        return particles

    def best_particle(self, particles):
        best_fit = float('-inf')
        best_particle = None
        for particle in particles : 
            if particle.personal_best_fitness >= best_fit : 
                best_particle = particle 
                best_fit =  particle.personal_best_fitness
        return best_particle
    
    def update(self, particles, params):
        controled_particles = self.controled_particles(particles, params)
        best_particle = self.best_particle(controled_particles)
        for particle in particles:
            if particle in controled_particles : 
                # Update personal best
                if particle.fitness > particle.personal_best_fitness:
                    particle.personal_best_fitness = particle.fitness
                    particle.personal_best_position = copy.deepcopy(particle.position)
            particle.informants_best_position = copy.deepcopy(best_particle.position)
            particle.informants_best_fitness = best_particle.personal_best_fitness

    def move(self, particles, params):
        for particle in particles:
            new_velocity = [0.0] * params.num_dimensions
            for i in range(params.num_dimensions):
                r1 = random.uniform(0, 1)
                r2 = random.uniform(0, 1)
                cognitive_component = params.c1 * r1 * (particle.personal_best_position[i] - particle.position[i])
                social_component = params.c2 * r2 * (particle.informants_best_position[i] - particle.position[i])
                new_velocity[i] = params.psi * particle.velocity[i] + cognitive_component + social_component
                particle.position[i] += new_velocity[i]

            particle.velocity = new_velocity
            particle.fitness = params.objective_function(particle.position)

    def pso(self, params):
        particles = self.init_particles(params)
        best_global_position = None
        best_global_fitness = float('-inf')
        best_fitness_progress = []
        best_position_progress = []

        for cycle in range(params.num_cycles):
            self.update(particles, params)
            self.move(particles, params)

            for particle in particles:
                if particle.fitness > best_global_fitness:
                    best_global_fitness = particle.personal_best_fitness
                    best_global_position = copy.deepcopy(particle.personal_best_position)

            best_fitness_progress.append(best_global_fitness)  
            best_position_progress.append(best_global_position)
        return best_global_position, best_global_fitness, best_position_progress, best_fitness_progress
# endregion

# region 2 : DE
class De:
    class Parameters:
        def __init__(self, objective_function, bounds, num_dimensions, num_population, scaling_factor, crossover_rate, max_generations):
            self.objective_function = objective_function
            self.bounds = bounds  # 2D
            self.num_dimensions = num_dimensions
            self.num_population = num_population
            self.scaling_factor = scaling_factor
            self.crossover_rate = crossover_rate
            self.max_generations = max_generations

    class Individual:
        def __init__(self, position, fitness):
            self.position = position
            self.fitness = fitness

    def init_population(self, params):
        population = []
        for _ in range(params.num_population):
            positions = []
            for bound in params.bounds:
                position = random.uniform(bound[0], bound[1])
                positions.append(position)
            new_individual = self.Individual(positions, params.objective_function(positions))
            population.append(new_individual)
        return population

    def mutate(self, target_individual_position, population, params):
        candidate_vector = copy.deepcopy(target_individual_position)
        dimension_to_mutate = random.randint(0, params.num_dimensions - 1)

        for i in range(params.num_dimensions):
            if i == dimension_to_mutate or random.random() < params.crossover_rate:
                candidate_vector[i] = target_individual_position[i] + params.scaling_factor * (population[0].position[i] - target_individual_position[i]) + params.scaling_factor * (population[1].position[i] - population[2].position[i])
                candidate_vector[i] = max(params.bounds[i][0], min(candidate_vector[i], params.bounds[i][1]))

        return candidate_vector

    def de(self, params):
        population = self.init_population(params)
        best_individual = max(population, key=lambda x: x.fitness)
        generation = 0
        best_fitness_progress = []  
        best_position_progress = []

        while generation < params.max_generations:
            new_population = []
            for target_individual in population:
                # Select three distinct individuals for mutation
                candidate_indices = list(range(params.num_population))
                candidate_indices.remove(population.index(target_individual))  
                a, b, c = random.sample(candidate_indices, 3)  
                random_individuals = [population[a], population[b], population[c]]  

                trial_vector = self.mutate(target_individual.position, random_individuals, params)
                trial_fitness = params.objective_function(trial_vector)

                # Selection : descendant or target_individual
                if trial_fitness >= target_individual.fitness:
                    new_individual = self.Individual(trial_vector, trial_fitness)
                    new_population.append(new_individual)
                else:
                    new_population.append(target_individual)

            population = new_population
            best_individual = max(population, key=lambda x: x.fitness)
            best_fitness_progress.append(best_individual.fitness)  
            best_position_progress.append(best_individual.position)
            generation += 1

        return best_individual.position, best_individual.fitness, best_position_progress, best_fitness_progress
# endregion

# region 3 : ABC
class Abc:
    class Parameters:
        def __init__(self, objective_function, bounds, num_dimensions, num_employed_bees, num_onlooker_bees, num_scout_bees, max_trials):
            self.objective_function = objective_function
            self.bounds = bounds
            self.num_dimensions = num_dimensions
            self.num_employed_bees = num_employed_bees
            self.num_onlooker_bees = num_onlooker_bees
            self.num_scout_bees = num_scout_bees
            self.max_trials = max_trials

    class FoodSource:
        def __init__(self, position, fitness, trials):
            self.position = position
            self.fitness = fitness  
            self.trials = trials

    def init_population(self, params):
        population = []
        for _ in range(params.num_employed_bees + params.num_onlooker_bees):
            positions = [random.uniform(bound[0], bound[1]) for bound in params.bounds]
            fitness = params.objective_function(positions)
            population.append(self.FoodSource(positions, fitness, 0))
        return population

    def select_food_sources(self, population):
        total_fitness = sum(fs.fitness for fs in population)
        selected = []
        for source in population:
            probability = source.fitness / total_fitness  # Inversez la fitness
            if random.random() < probability:
                selected.append(source)
        return selected

    def update_food_source(self, source, params):
        position = [p + random.uniform(-1, 1) for p in source.position]
        for i in range(params.num_dimensions):
            position[i] = max(params.bounds[i][0], min(position[i], params.bounds[i][1]))
        fitness = params.objective_function(position)
        source.position = position
        source.fitness = fitness  

    def scout_bees_phase(self, population, params):
        for source in population:
            if source.trials >= params.max_trials:
                source.position = [random.uniform(0, 1) for _ in range(params.num_dimensions)]
                source.fitness = params.objective_function(source.position)
                source.trials = 0

    def abc(self, params):
        population = self.init_population(params)
        best_source = max(population, key=lambda x: x.fitness)  
        best_fitness_progress = []  
        best_position_progress = []

        for _ in range(params.num_scout_bees):
            self.scout_bees_phase(population, params)

        for _ in range(params.max_trials):
            onlooker_sources = self.select_food_sources(population)
            for source in onlooker_sources:
                self.update_food_source(source, params)
            best_source = max(population, key=lambda x: x.fitness) 
            best_fitness_progress.append(best_source.fitness)  
            best_position_progress.append(best_source.position)
        return best_source.position, best_source.fitness, best_position_progress, best_fitness_progress
# endregion
