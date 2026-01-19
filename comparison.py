"""
Script de comparaison et benchmark entre mono-thread et multi-thread.

Ce script :
1. Exécute les deux versions avec différentes configurations
2. Mesure les temps d'exécution (plusieurs runs)
3. Calcule moyenne, écart-type, speedup
4. Sauvegarde les résultats en JSON
5. Génère automatiquement les graphiques
"""

import time
import json
import os
import statistics
import argparse
from mono_thread import monte_carlo_pi_mono
from multi_thread import monte_carlo_pi_multi


def benchmark_mono(iterations, num_runs=10):
    """
    Benchmark de la version mono-thread.
    
    Args:
        iterations: Nombre d'itérations
        num_runs: Nombre de runs pour calculer la moyenne
        
    Returns:
        Dict avec les résultats
    """
    print(f"\n🔄 Benchmark MONO-THREAD ({num_runs} runs)...")
    times = []
    
    for run in range(num_runs):
        start = time.time()
        pi_estimate = monte_carlo_pi_mono(iterations)
        end = time.time()
        elapsed = end - start
        times.append(elapsed)
        print(f"  Run {run + 1}/{num_runs}: {elapsed:.4f}s")
    
    avg_time = statistics.mean(times)
    std_time = statistics.stdev(times) if len(times) > 1 else 0
    
    print(f"  ✅ Moyenne: {avg_time:.4f}s (±{std_time:.4f}s)")
    
    return {
        'iterations': iterations,
        'num_runs': num_runs,
        'times': times,
        'avg_time': avg_time,
        'std_time': std_time,
        'min_time': min(times),
        'max_time': max(times)
    }


def benchmark_multi(iterations, num_threads, num_runs=10):
    """
    Benchmark de la version multi-thread.
    
    Args:
        iterations: Nombre d'itérations
        num_threads: Nombre de threads
        num_runs: Nombre de runs pour calculer la moyenne
        
    Returns:
        Dict avec les résultats
    """
    print(f"\n🔄 Benchmark MULTI-THREAD avec {num_threads} threads ({num_runs} runs)...")
    times = []
    
    for run in range(num_runs):
        start = time.time()
        pi_estimate = monte_carlo_pi_multi(iterations, num_threads)
        end = time.time()
        elapsed = end - start
        times.append(elapsed)
        print(f"  Run {run + 1}/{num_runs}: {elapsed:.4f}s")
    
    avg_time = statistics.mean(times)
    std_time = statistics.stdev(times) if len(times) > 1 else 0
    
    print(f"  ✅ Moyenne: {avg_time:.4f}s (±{std_time:.4f}s)")
    
    return {
        'iterations': iterations,
        'num_threads': num_threads,
        'num_runs': num_runs,
        'times': times,
        'avg_time': avg_time,
        'std_time': std_time,
        'min_time': min(times),
        'max_time': max(times)
    }


def compare_performance(iterations=10_000_000, max_threads=8, num_runs=10):
    """
    Compare les performances mono vs multi avec différentes configurations.
    
    Args:
        iterations: Nombre d'itérations
        max_threads: Nombre maximum de threads à tester
        num_runs: Nombre de runs par configuration
        
    Returns:
        Dict avec tous les résultats
    """
    print("=" * 70)
    print("COMPARAISON MONO-THREAD vs MULTI-THREAD")
    print("=" * 70)
    print(f"Itérations par test : {iterations:,}")
    print(f"Runs par config     : {num_runs}")
    print(f"Threads testés      : 1, 2, 4, ..., {max_threads}")
    print("=" * 70)
    
    # Benchmark mono-thread
    mono_results = benchmark_mono(iterations, num_runs)
    
    # Benchmark multi-thread avec différents nombres de threads
    multi_results = []
    thread_counts = [2**i for i in range(1, int(max_threads).bit_length() + 1) if 2**i <= max_threads]
    
    for num_threads in thread_counts:
        result = benchmark_multi(iterations, num_threads, num_runs)
        result['speedup'] = mono_results['avg_time'] / result['avg_time']
        result['efficiency'] = result['speedup'] / num_threads
        multi_results.append(result)
    
    # Résumé
    print("\n" + "=" * 70)
    print("RÉSUMÉ DES RÉSULTATS")
    print("=" * 70)
    print(f"{'Configuration':<20} {'Temps (s)':<15} {'Speedup':<12} {'Efficacité':<12}")
    print("-" * 70)
    print(f"{'Mono-thread':<20} {mono_results['avg_time']:<15.4f} {'1.00x':<12} {'100%':<12}")
    
    for result in multi_results:
        threads = result['num_threads']
        time_str = f"{result['avg_time']:.4f}"
        speedup_str = f"{result['speedup']:.2f}x"
        efficiency_str = f"{result['efficiency'] * 100:.1f}%"
        print(f"{f'{threads} threads':<20} {time_str:<15} {speedup_str:<12} {efficiency_str:<12}")
    
    print("=" * 70)
    
    # Sauvegarder les résultats
    results = {
        'iterations': iterations,
        'num_runs': num_runs,
        'mono_thread': mono_results,
        'multi_thread': multi_results
    }
    
    # Créer le dossier results s'il n'existe pas
    os.makedirs('results', exist_ok=True)
    
    # Sauvegarder en JSON
    output_file = 'results/benchmark_results.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Résultats sauvegardés dans : {output_file}")
    
    return results


def main():
    """Fonction principale."""
    parser = argparse.ArgumentParser(description='Comparaison Mono vs Multi-Thread')
    parser.add_argument('--iterations', type=int, default=10_000_000,
                        help='Nombre d\'itérations (défaut: 10,000,000)')
    parser.add_argument('--max-threads', type=int, default=8,
                        help='Nombre maximum de threads à tester (défaut: 8)')
    parser.add_argument('--runs', type=int, default=10,
                        help='Nombre de runs par configuration (défaut: 10)')
    args = parser.parse_args()
    
    # Exécuter la comparaison
    results = compare_performance(
        iterations=args.iterations,
        max_threads=args.max_threads,
        num_runs=args.runs
    )
    
    # Générer les graphiques
    print("\n📊 Génération des graphiques...")
    try:
        import visualize_results
        visualize_results.generate_all_graphs('results/benchmark_results.json')
        print("✅ Graphiques générés dans le dossier 'graphs/'")
    except ImportError:
        print("⚠️  Module matplotlib non disponible. Installez-le pour générer les graphiques.")
    except Exception as e:
        print(f"⚠️  Erreur lors de la génération des graphiques : {e}")


if __name__ == "__main__":
    main()
