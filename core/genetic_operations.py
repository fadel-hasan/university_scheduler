import random

class GeneticOperations:
    """Genetic operations like crossover and selection"""
    def __init__(self, individual_generator, fitness_calculator, data_collector):
        self.individual_generator = individual_generator
        self.fitness_calculator = fitness_calculator
        self.data_collector = data_collector

    def crossover(self, parent1, parent2):
        """Crossover operation between two parents to produce two children"""

        if not parent1 or not parent2:
            return parent1, parent2

        if len(parent1) < 2 or len(parent2) < 2:
            return parent1, parent2
        
        point = random.randint(1, min(len(parent1), len(parent2)) - 1)
        child1 = parent1[:point] + parent2[point:]
        child2 = parent2[:point] + parent1[point:]
        return child1, child2

    def evolve_population(self, population, elite_size, mutation_rate, population_size):
        """Evolve population through one generation with guaranteed valid individuals"""
        fitness_cache = {}
        valid_population = []
    
        for ind in population:
            try:
                if ind and len(ind) > 0:
                    fitness = self.fitness_calculator.calculate_fitness(ind)
                    fitness_cache[id(ind)] = fitness
                    valid_population.append(ind)
                else:

                    new_ind = self.individual_generator.generate_individual()
                    fitness_cache[id(new_ind)] = self.fitness_calculator.calculate_fitness(new_ind)
                    valid_population.append(new_ind)
            except Exception as e:
                print(f"Error calculating fitness: {e}")
                new_ind = self.individual_generator.generate_individual()
                fitness_cache[id(new_ind)] = self.fitness_calculator.calculate_fitness(new_ind)
                valid_population.append(new_ind)
    
        sorted_population = sorted(valid_population, key=lambda ind: fitness_cache[id(ind)], reverse=True)
    
        new_population = sorted_population[:elite_size]
    
        while len(new_population) < population_size:
            try:

                pool_size = max(len(sorted_population) // 2, 2)
                parents = random.sample(sorted_population[:pool_size], 2)
                child1, child2 = self.crossover(parents[0], parents[1])
    
                if child1:
                    mutated_child1 = self.individual_generator.mutate(child1, mutation_rate)
                    new_population.append(mutated_child1)
    
                if len(new_population) < population_size and child2:
                    mutated_child2 = self.individual_generator.mutate(child2, mutation_rate)
                    new_population.append(mutated_child2)
    
            except Exception as e:
                print(f"Error in reproduction: {e}")
                new_ind = self.individual_generator.generate_individual()
                new_population.append(new_ind)
    
        final_population = []
        for ind in new_population:
            if ind and len(ind) == len(self.data_collector.courses):
                final_population.append(ind)
            else:
                repaired = self.individual_generator.generate_individual()
                final_population.append(repaired)
    
        return final_population[:population_size]
