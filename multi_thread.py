"""
Simulation Monte Carlo pour calculer Pi - VERSION MULTI-THREAD

Cette version utilise plusieurs threads pour paralléliser le calcul :
- Divise les itérations entre plusieurs threads
- Chaque thread travaille indépendamment
- Utilise Queue pour collecter les résultats (thread-safe)
- Plus rapide sur CPU multi-cœur
"""

import random
import time
import threading
import queue
import argparse
import os


def worker(iterations, result_queue, thread_id):
    """
    Fonction worker exécutée par chaque thread.
    
    Chaque thread génère ses propres points aléatoires et compte
    combien tombent dans le cercle. Le résultat est mis dans une
    queue thread-safe.
    
    Args:
        iterations: Nombre d'itérations pour ce thread
        result_queue: Queue pour stocker le résultat
        thread_id: Identifiant du thread (pour debug)
    """
    inside_circle = 0
    
    # Générer des points aléatoires
    for _ in range(iterations):
        x = random.random()
        y = random.random()
        
        if x * x + y * y <= 1:
            inside_circle += 1
    
    # Mettre le résultat dans la queue (thread-safe)
    result_queue.put(inside_circle)


def monte_carlo_pi_multi(total_iterations, num_threads):
    """
    Calcule Pi en utilisant la méthode Monte Carlo (version multi-thread).
    
    Args:
        total_iterations: Nombre total de points à générer
        num_threads: Nombre de threads à utiliser
        
    Returns:
        Estimation de Pi
    """
    # Diviser les itérations entre les threads
    iterations_per_thread = total_iterations // num_threads
    remaining_iterations = total_iterations % num_threads
    
    # Créer une queue thread-safe pour collecter les résultats
    result_queue = queue.Queue()
    
    # Créer et démarrer les threads
    threads = []
    for i in range(num_threads):
        # Le dernier thread prend les itérations restantes
        iterations = iterations_per_thread
        if i == num_threads - 1:
            iterations += remaining_iterations
        
        t = threading.Thread(target=worker, args=(iterations, result_queue, i))
        threads.append(t)
        t.start()
    
    # Attendre que tous les threads terminent
    for t in threads:
        t.join()
    
    # Collecter les résultats de tous les threads
    total_inside = 0
    for _ in range(num_threads):
        total_inside += result_queue.get()
    
    # Calculer l'estimation de Pi
    pi_estimate = 4 * total_inside / total_iterations
    return pi_estimate


def main():
    """Fonction principale pour exécuter la simulation multi-thread."""
    parser = argparse.ArgumentParser(description='Simulation Monte Carlo - Multi-Thread')
    parser.add_argument('--iterations', type=int, default=10_000_000,
                        help='Nombre d\'itérations (défaut: 10,000,000)')
    parser.add_argument('--threads', type=int, default=None,
                        help='Nombre de threads (défaut: nombre de CPU)')
    args = parser.parse_args()
    
    iterations = args.iterations
    
    # Déterminer le nombre de threads
    if args.threads is None:
        num_threads = os.cpu_count() or 4
    else:
        num_threads = args.threads
    
    print("=" * 60)
    print("SIMULATION MONTE CARLO - MULTI-THREAD")
    print("=" * 60)
    print(f"Nombre d'itérations  : {iterations:,}")
    print(f"Nombre de threads    : {num_threads}")
    print(f"Nombre de CPU        : {os.cpu_count()}")
    print(f"Itérations/thread    : {iterations // num_threads:,}")
    print("Démarrage du calcul...")
    print()
    
    # Mesurer le temps d'exécution
    start_time = time.time()
    pi_estimate = monte_carlo_pi_multi(iterations, num_threads)
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
        'num_threads': num_threads,
        'iterations_per_second': iterations / execution_time
    }


if __name__ == "__main__":
    main()
