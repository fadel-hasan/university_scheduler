from datetime import datetime
from sqlalchemy.orm import Session
from db.models import Schedule, ScheduleSlot

from .data_collector import DataCollector
from .conflict_checker import ConflictChecker
from .individual_generator import IndividualGenerator
from .fitness_calculator import FitnessCalculator
from .genetic_operations import GeneticOperations
from .schedule_presenter import SchedulePresenter

class GeneticScheduler:
    """Main object to run the genetic algorithm"""
    def __init__(self, session: Session, academic_year_id: int, population_size=50, generations=100, mutation_rate=0.3, elite_size=0):

        self.data_collector = DataCollector(session, academic_year_id)
        self.teacher_slot_map = self.data_collector.build_teacher_availability_map()
        self.external_conflicts_map = self.data_collector.build_external_conflicts_map()

        self.conflict_checker = ConflictChecker(self.data_collector)
        self.individual_generator = IndividualGenerator(self.data_collector, self.conflict_checker)
        self.fitness_calculator = FitnessCalculator(self.conflict_checker, self.individual_generator, self.data_collector)
        self.genetic_operations = GeneticOperations(self.individual_generator, self.fitness_calculator, self.data_collector)
        self.presenter = SchedulePresenter(self.data_collector, self.conflict_checker)

        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.elite_size = elite_size
        self.session = session
        self.academic_year_id = academic_year_id
        self.academic_year = self.data_collector.academic_year

    def run(self, progress_callback=None):
        """Run the complete genetic algorithm"""
        self.data_collector.external_conflicts_map = self.data_collector.build_external_conflicts_map()
        self.external_conflicts_map = self.data_collector.external_conflicts_map

        population = [self.individual_generator.generate_individual() for _ in range(self.population_size)]
        best = None
        best_fitness = 0
        print(f"Starting genetic algorithm with {self.population_size} individuals and {self.generations} generations")
        for generation in range(self.generations):
            try:

                population = self.genetic_operations.evolve_population(population, self.elite_size, self.mutation_rate, self.population_size)

                valid_population = []
                fitnesses = []
                for ind in population:
                    if ind and len(ind) > 0:  
                        try:
                            fitness = self.fitness_calculator.calculate_fitness(ind)
                            if isinstance(fitness, (int, float)) and not (isinstance(fitness, bool)):
                                fitnesses.append(fitness)
                                valid_population.append(ind)
                            else:
                                print(f"Warning: Invalid fitness value in generation {generation}: {fitness}")
                                fitnesses.append(0.0)
                                valid_population.append(ind)
                        except Exception as e:
                            print(f"Error calculating fitness in generation {generation}: {e}")
                            fitnesses.append(0.0)
                            valid_population.append(ind)
                if valid_population and fitnesses:
                    max_fit = max(fitnesses)
                    avg_fit = sum(fitnesses) / len(fitnesses)
                    if max_fit > best_fitness:
                        best_fitness = max_fit
                        best = valid_population[fitnesses.index(max_fit)]
                        
                    if progress_callback:
                        try:
                            progress_callback({
                                'generation': generation,
                                'best_fitness': best_fitness,
                                'avg_fitness': avg_fit,
                                'max_fitness': max_fit
                            })
                        except Exception as e:
                            print(f"Error in progress callback: {e}")

                    if generation % 10 == 0:
                        print(f"Generation {generation}: Best fitness = {max_fit:.4f}, Average fitness = {avg_fit:.4f}")
                    if best_fitness == 1:
                        print(f"Perfect solution found in generation {generation}")
                        break
                else:
                    print(f"Warning: No valid individuals in generation {generation}")
                    
                    population = [self.individual_generator.generate_individual() for _ in range(self.population_size)]
            except Exception as e:
                print(f"Error in generation {generation}: {e}")
                
                population = [self.individual_generator.generate_individual() for _ in range(self.population_size)]
        print(f"Algorithm finished. Best fitness score: {best_fitness:.4f}")
        return best, best_fitness

    def save_schedule(self, individual, name=None):
        """Save schedule to database"""
        
        schedule = Schedule(
            name=name or f"Schedule {self.academic_year.name} - {datetime.now().strftime('%Y-%m-%d')}",
            academic_year_id=self.academic_year_id,
            created_at=datetime.now().date(),
            fitness_score=int(self.fitness_calculator.calculate_fitness(individual) * 100)  
        )
        self.session.add(schedule)
        self.session.flush()  

        for slot in individual:
            schedule_slot = ScheduleSlot(
                schedule_id=schedule.id,
                course_id=slot['course'].id,
                teacher_id=slot['teacher'].id,
                classroom_id=slot['classroom'].id,
                day_of_week=slot['day'],
                start_time=slot['start_time'],
                end_time=slot['end_time']
            )
            self.session.add(schedule_slot)
        self.session.commit()
        return schedule
