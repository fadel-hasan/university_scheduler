from core.genetic_algorithm import GeneticScheduler


def generate_schedule(session, academic_year_id, population_size=50, generations=100, mutation_rate=0.1):
    scheduler = GeneticScheduler(
        session=session,
        academic_year_id=academic_year_id,
        population_size=population_size,
        generations=generations,
        mutation_rate=mutation_rate
    )
    return scheduler.run()
