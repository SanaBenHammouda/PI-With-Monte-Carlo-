"""
Simulation Monte Carlo pour calculer Pi - VERSION MONO-THREAD

Cette version utilise une approche séquentielle simple :
- Une seule boucle qui traite toutes les itérations
- Pas de parallélisme
- Simple mais lent sur grandes données
"""

import random
import time
import argparse


def monte_carlo_pi_mono(iterations):
    """
    Calcule Pi en utilisant la méthode Monte Carlo (version mono-thread).
    
    Principe :
    1. Générer des points aléatoires (x, y) dans le carré [0,1] × [0,1]
    2. Compter combien tombent dans le quart de cercle (x² + y² ≤ 1)
    3. Pi ≈ 4 × (points dans cercle / total points)
    
    Args:
        iterations: Nombre de points aléatoires à générer
        
    Returns:
        Estimation de Pi
    """
    inside_circle = 0
    
    # Traiter toutes les itérations séquentiellement
    for _ in range(iterations):
        # Générer un point aléatoire
        x = random.random()
        y = random.random()
        
        # Vérifier si le point est dans le quart de cercle
        if x * x + y * y <= 1:
            inside_circle += 1
    
    # Calculer l'estimation de Pi
    pi_estimate = 4 * inside_circle / iterations
    return pi_estimate


def main():
    """Fonction principale pour exécuter la simulation mono-thread."""
    parser = argparse.ArgumentParser(description='Simulation Monte Carlo - Mono-Thread')
    parser.add_argument('--iterations', type=int, default=10_000_000,
                        help='Nombre d\'itérations (défaut: 10,000,000)')
    args = parser.parse_args()
    
    iterations = args.iterations
    
    print("=" * 60)
    print("SIMULATION MONTE CARLO - MONO-THREAD")
    print("=" * 60)
    print(f"Nombre d'itérations : {iterations:,}")
    print("Démarrage du calcul...")
    print()
    
    # Mesurer le temps d'exécution
    start_time = time.time()
    pi_estimate = monte_carlo_pi_mono(iterations)
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
        'iterations_per_second': iterations / execution_time
    }


if __name__ == "__main__":
    main()
