"""
Monitoring CPU en temps réel pendant l'exécution.

Ce script permet de :
1. Monitorer l'utilisation CPU pendant l'exécution
2. Comparer l'utilisation entre mono-thread et multi-thread
3. Générer des graphiques d'utilisation CPU
"""

import time
import threading
import psutil
import matplotlib.pyplot as plt
import argparse
import os
from mono_thread import monte_carlo_pi_mono
from multi_thread import monte_carlo_pi_multi
from multiprocessing_version import monte_carlo_pi_multiprocessing
import multiprocessing as mp


class CPUMonitor:
    """
    Classe pour monitorer l'utilisation CPU en temps réel.
    """
    
    def __init__(self, interval=0.1):
        """
        Initialise le moniteur CPU.
        
        Args:
            interval: Intervalle de mesure en secondes
        """
        self.interval = interval
        self.cpu_percentages = []
        self.timestamps = []
        self.monitoring = False
        self.monitor_thread = None
        self.start_time = None
    
    def _monitor_loop(self):
        """Boucle de monitoring (exécutée dans un thread séparé)."""
        self.start_time = time.time()
        
        while self.monitoring:
            cpu_percent = psutil.cpu_percent(interval=self.interval, percpu=False)
            elapsed = time.time() - self.start_time
            
            self.cpu_percentages.append(cpu_percent)
            self.timestamps.append(elapsed)
    
    def start(self):
        """Démarre le monitoring."""
        self.monitoring = True
        self.cpu_percentages = []
        self.timestamps = []
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop(self):
        """Arrête le monitoring."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
    
    def get_stats(self):
        """Retourne les statistiques d'utilisation CPU."""
        if not self.cpu_percentages:
            return {}
        
        return {
            'avg_cpu': sum(self.cpu_percentages) / len(self.cpu_percentages),
            'max_cpu': max(self.cpu_percentages),
            'min_cpu': min(self.cpu_percentages),
            'duration': self.timestamps[-1] if self.timestamps else 0,
            'samples': len(self.cpu_percentages)
        }


def benchmark_with_monitoring(func, *args, label="Test"):
    """
    Exécute une fonction en monitorant l'utilisation CPU.
    
    Args:
        func: Fonction à exécuter
        *args: Arguments de la fonction
        label: Label pour l'affichage
        
    Returns:
        Tuple (résultat, stats CPU, temps d'exécution)
    """
    print(f"\n{'=' * 60}")
    print(f"BENCHMARK : {label}")
    print(f"{'=' * 60}")
    
    # Créer et démarrer le moniteur
    monitor = CPUMonitor(interval=0.1)
    monitor.start()
    
    # Exécuter la fonction
    start_time = time.time()
    result = func(*args)
    end_time = time.time()
    
    # Arrêter le monitoring
    time.sleep(0.2)  # Attendre un peu pour capturer les dernières mesures
    monitor.stop()
    
    execution_time = end_time - start_time
    stats = monitor.get_stats()
    
    # Afficher les résultats
    print(f"Temps d'exécution    : {execution_time:.4f}s")
    print(f"CPU moyen            : {stats['avg_cpu']:.1f}%")
    print(f"CPU max              : {stats['max_cpu']:.1f}%")
    print(f"CPU min              : {stats['min_cpu']:.1f}%")
    print(f"Échantillons         : {stats['samples']}")
    
    return result, monitor, execution_time


def compare_cpu_usage(iterations=5_000_000):
    """
    Compare l'utilisation CPU entre les différentes versions.
    
    Args:
        iterations: Nombre d'itérations pour chaque test
    """
    print("\n" + "🔬" * 30)
    print("COMPARAISON UTILISATION CPU")
    print("🔬" * 30)
    print(f"\nItérations par test : {iterations:,}")
    print(f"Nombre de CPU       : {os.cpu_count()}")
    
    results = {}
    
    # Test 1 : Mono-thread
    print("\n" + "=" * 60)
    print("TEST 1/3 : MONO-THREAD")
    print("=" * 60)
    _, monitor_mono, time_mono = benchmark_with_monitoring(
        monte_carlo_pi_mono, iterations, label="Mono-Thread"
    )
    results['mono'] = {
        'monitor': monitor_mono,
        'time': time_mono,
        'label': 'Mono-Thread'
    }
    
    # Test 2 : Multi-thread
    num_threads = 4
    print("\n" + "=" * 60)
    print(f"TEST 2/3 : MULTI-THREAD ({num_threads} threads)")
    print("=" * 60)
    _, monitor_multi, time_multi = benchmark_with_monitoring(
        monte_carlo_pi_multi, iterations, num_threads, label=f"Multi-Thread ({num_threads} threads)"
    )
    results['multi'] = {
        'monitor': monitor_multi,
        'time': time_multi,
        'label': f'Multi-Thread ({num_threads}T)'
    }
    
    # Test 3 : Multiprocessing
    num_processes = 4
    print("\n" + "=" * 60)
    print(f"TEST 3/3 : MULTIPROCESSING ({num_processes} processus)")
    print("=" * 60)
    _, monitor_mp, time_mp = benchmark_with_monitoring(
        monte_carlo_pi_multiprocessing, iterations, num_processes, 
        label=f"Multiprocessing ({num_processes} processus)"
    )
    results['multiprocessing'] = {
        'monitor': monitor_mp,
        'time': time_mp,
        'label': f'Multiprocessing ({num_processes}P)'
    }
    
    # Générer les graphiques
    plot_cpu_comparison(results)
    
    # Résumé
    print("\n" + "=" * 60)
    print("RÉSUMÉ")
    print("=" * 60)
    print(f"{'Version':<25} {'Temps (s)':<12} {'CPU Moyen':<12} {'Speedup':<10}")
    print("-" * 60)
    
    for key, data in results.items():
        stats = data['monitor'].get_stats()
        speedup = time_mono / data['time']
        print(f"{data['label']:<25} {data['time']:<12.4f} {stats['avg_cpu']:<12.1f}% {speedup:<10.2f}x")
    
    print("=" * 60)


def plot_cpu_comparison(results):
    """
    Génère des graphiques de comparaison d'utilisation CPU.
    
    Args:
        results: Dictionnaire des résultats avec monitors
    """
    print("\n📊 Génération des graphiques d'utilisation CPU...")
    
    # Créer le dossier graphs s'il n'existe pas
    os.makedirs('graphs', exist_ok=True)
    
    # Graphique 1 : Utilisation CPU au fil du temps
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))
    
    colors = {'mono': 'red', 'multi': 'green', 'multiprocessing': 'blue'}
    
    for idx, (key, data) in enumerate(results.items()):
        monitor = data['monitor']
        ax = axes[idx]
        
        ax.plot(monitor.timestamps, monitor.cpu_percentages, 
                color=colors[key], linewidth=2, label=data['label'])
        ax.fill_between(monitor.timestamps, monitor.cpu_percentages, 
                        alpha=0.3, color=colors[key])
        ax.set_ylabel('CPU (%)', fontsize=11)
        ax.set_title(f'{data["label"]} - Utilisation CPU', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0, 100)
        
        # Ajouter ligne de moyenne
        stats = monitor.get_stats()
        ax.axhline(y=stats['avg_cpu'], color=colors[key], 
                  linestyle='--', linewidth=1, alpha=0.7,
                  label=f'Moyenne: {stats["avg_cpu"]:.1f}%')
        ax.legend(loc='upper right')
    
    axes[-1].set_xlabel('Temps (secondes)', fontsize=11)
    plt.suptitle('Comparaison Utilisation CPU : Mono vs Multi vs Multiprocessing', 
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('graphs/cpu_usage_timeline.png', dpi=300)
    print("  ✅ Graphique sauvegardé : graphs/cpu_usage_timeline.png")
    plt.close()
    
    # Graphique 2 : Comparaison moyenne CPU
    fig, ax = plt.subplots(figsize=(10, 6))
    
    labels = [data['label'] for data in results.values()]
    avg_cpus = [data['monitor'].get_stats()['avg_cpu'] for data in results.values()]
    colors_list = [colors[key] for key in results.keys()]
    
    bars = ax.bar(labels, avg_cpus, color=colors_list, alpha=0.7)
    ax.set_ylabel('Utilisation CPU Moyenne (%)', fontsize=12)
    ax.set_title('Comparaison Utilisation CPU Moyenne', fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    ax.set_ylim(0, 100)
    
    # Ajouter les valeurs sur les barres
    for bar, cpu in zip(bars, avg_cpus):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 2,
                f'{cpu:.1f}%', ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('graphs/cpu_usage_comparison.png', dpi=300)
    print("  ✅ Graphique sauvegardé : graphs/cpu_usage_comparison.png")
    plt.close()
    
    print("✅ Graphiques CPU générés avec succès !")


def main():
    """Fonction principale."""
    parser = argparse.ArgumentParser(description='Monitoring CPU en temps réel')
    parser.add_argument('--iterations', type=int, default=5_000_000,
                        help='Nombre d\'itérations (défaut: 5,000,000)')
    args = parser.parse_args()
    
    compare_cpu_usage(iterations=args.iterations)


if __name__ == "__main__":
    # Nécessaire pour Windows avec multiprocessing
    mp.freeze_support()
    main()
