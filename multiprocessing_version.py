"""
Simulation Monte Carlo pour calculer Pi - VERSION MULTIPROCESSING

Cette version utilise multiprocessing au lieu de threading pour contourner le GIL :
- Vrai parallélisme sur CPU multi-cœur
- Chaque processus a son propre interpréteur Python
- Speedup réel de 4x sur 4 cœurs (pas limité par le GIL)
- Idéal pour tâches CPU-bound intensives
"""

import random
import time
import multiprocessing as mp
import argparse
import os


def worker_process(iterations):
    """
    Fonction worker exécutée par chaque processus.
    
    Chaque processus génère ses propres points aléatoires et compte
    combien tombent dans le cercle. Le résultat est retourné directement.
    
    Args:
        iterations: Nombre d'itérations pour ce processus
        
    Returns:
        Nombre de points dans le cercle
    """
    inside_circle = 0
    
    # Générer des points aléatoires
    for _ in range(iterations):
        x = random.random()
        y = random.random()
        
        if x * x + y * y <= 1:
            inside_circle += 1
    
    return inside_circle


def monte_carlo_pi_multiprocessing(total_iterations, num_processes):
    """
    Calcule Pi en utilisant la méthode Monte Carlo (version multiprocessing).
    
    Args:
        total_iterations: Nombre total de points à générer
        num_processes: Nombre de processus à utiliser
        
    Returns:
        Estimation de Pi
    """
    # Diviser les itérations entre les processus
    iterations_per_process = total_iterations // num_processes
    remaining_iterations = total_iterations % num_processes
    
    # Créer la liste des tâches
    tasks = [iterations_per_process] * num_processes
    if remaining_iterations > 0:
        tasks[-1] += remaining_iterations
    
    # Créer un pool de processus et exécuter en parallèle
    with mp.Pool(processes=num_processes) as pool:
        results = pool.map(worker_process, tasks)
    
    # Sommer les résultats de tous les processus
    total_inside = sum(results)
    
    # Calculer l'estimation de Pi
    pi_estimate = 4 * total_inside / total_iterations
    return pi_estimate


def main():
    """Fonction principale pour exécuter la simulation multiprocessing."""
    parser = argparse.ArgumentParser(description='Simulation Monte Carlo - Multiprocessing')
    parser.add_argument('--iterations', type=int, default=10_000_000,
                        help='Nombre d\'itérations (défaut: 10,000,000)')
    parser.add_argument('--processes', type=int, default=None,
                        help='Nombre de processus (défaut: nombre de CPU)')
    args = parser.parse_args()
    
    iterations = args.iterations
    
    # Déterminer le nombre de processus
    if args.processes is None:
        num_processes = os.cpu_count() or 4
    else:
        num_processes = args.processes
    
    print("=" * 60)
    print("SIMULATION MONTE CARLO - MULTIPROCESSING")
    print("=" * 60)
    print(f"Nombre d'itérations  : {iterations:,}")
    print(f"Nombre de processus  : {num_processes}")
    print(f"Nombre de CPU        : {os.cpu_count()}")
    print(f"Itérations/processus : {iterations // num_processes:,}")
    print("\n🚀 AVANTAGE : Contourne le GIL de Python !")
    print("   → Vrai parallélisme sur CPU multi-cœur")
    print("   → Speedup réel proche du nombre de cœurs")
    print("\nDémarrage du calcul...")
    print()
    
    # Mesurer le temps d'exécution
    start_time = time.time()
    pi_estimate = monte_carlo_pi_multiprocessing(iterations, num_processes)
    end_time = time.time()
    
    execution_time = end_time - start_time
    
    # Afficher les résultats
    print("=" * 60)
    print("RÉSULTATS")
    print("=" * 60)
    print(f"Estimation de Pi     : {pi_estimate:.8f}")
    print(f"Valeur réelle de Pi  : {3.14159265:.8f}")
    print(f"Erreur               : {abs(pi_estimate - 3.14159265):.8f}")
    print(f"Temps d'exécution    : {execution_time:.4f} secondes")
    print(f"Itérations/seconde   : {iterations / execution_time:,.0f}")
    print("=" * 60)
    
    return {
        'pi_estimate': pi_estimate,
        'execution_time': execution_time,
        'iterations': iterations,
        'num_processes': num_processes,
        'iterations_per_second': iterations / execution_time
    }


if __name__ == "__main__":
    # Nécessaire pour Windows
    mp.freeze_support()
    main()
