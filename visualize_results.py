"""
Script pour générer les graphiques de comparaison.

Génère :
1. Temps d'exécution mono vs multi
2. Speedup en fonction du nombre de threads
3. Scalabilité et efficacité
4. Comparaison détaillée
"""

import json
import matplotlib.pyplot as plt
import numpy as np
import os


def load_results(filename='results/benchmark_results.json'):
    """Charge les résultats depuis le fichier JSON."""
    with open(filename, 'r') as f:
        return json.load(f)


def plot_execution_time_comparison(results, output_dir='graphs'):
    """
    Graphique 1 : Comparaison des temps d'exécution.
    """
    mono_time = results['mono_thread']['avg_time']
    mono_std = results['mono_thread']['std_time']
    
    thread_counts = [r['num_threads'] for r in results['multi_thread']]
    multi_times = [r['avg_time'] for r in results['multi_thread']]
    multi_stds = [r['std_time'] for r in results['multi_thread']]
    
    # Ajouter mono-thread (1 thread)
    all_threads = [1] + thread_counts
    all_times = [mono_time] + multi_times
    all_stds = [mono_std] + multi_stds
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(range(len(all_threads)), all_times, 
                   yerr=all_stds, capsize=5, alpha=0.7, 
                   color=['red'] + ['green'] * len(thread_counts))
    
    plt.xlabel('Nombre de Threads', fontsize=12)
    plt.ylabel('Temps d\'exécution (secondes)', fontsize=12)
    plt.title('Comparaison Temps d\'Exécution : Mono-Thread vs Multi-Thread', fontsize=14, fontweight='bold')
    plt.xticks(range(len(all_threads)), all_threads)
    plt.grid(axis='y', alpha=0.3)
    
    # Ajouter les valeurs sur les barres
    for i, (bar, time) in enumerate(zip(bars, all_times)):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                f'{time:.2f}s', ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(f'{output_dir}/execution_time_comparison.png', dpi=300)
    print(f"  ✅ Graphique sauvegardé : {output_dir}/execution_time_comparison.png")
    plt.close()


def plot_speedup(results, output_dir='graphs'):
    """
    Graphique 2 : Speedup en fonction du nombre de threads.
    """
    thread_counts = [r['num_threads'] for r in results['multi_thread']]
    speedups = [r['speedup'] for r in results['multi_thread']]
    
    # Speedup idéal (linéaire)
    ideal_speedup = thread_counts
    
    plt.figure(figsize=(10, 6))
    plt.plot([1] + thread_counts, [1.0] + speedups, 'o-', linewidth=2, 
             markersize=8, label='Speedup réel', color='blue')
    plt.plot([1] + thread_counts, [1.0] + ideal_speedup, '--', linewidth=2, 
             label='Speedup idéal (linéaire)', color='gray', alpha=0.7)
    
    plt.xlabel('Nombre de Threads', fontsize=12)
    plt.ylabel('Speedup (×)', fontsize=12)
    plt.title('Speedup en Fonction du Nombre de Threads', fontsize=14, fontweight='bold')
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    
    # Ajouter les valeurs
    for threads, speedup in zip(thread_counts, speedups):
        plt.text(threads, speedup + 0.1, f'{speedup:.2f}×', 
                ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/speedup_vs_threads.png', dpi=300)
    print(f"  ✅ Graphique sauvegardé : {output_dir}/speedup_vs_threads.png")
    plt.close()


def plot_efficiency(results, output_dir='graphs'):
    """
    Graphique 3 : Efficacité parallèle.
    """
    thread_counts = [r['num_threads'] for r in results['multi_thread']]
    efficiencies = [r['efficiency'] * 100 for r in results['multi_thread']]
    
    plt.figure(figsize=(10, 6))
    plt.plot(thread_counts, efficiencies, 'o-', linewidth=2, 
             markersize=8, color='purple')
    plt.axhline(y=100, color='gray', linestyle='--', linewidth=2, 
                label='Efficacité idéale (100%)', alpha=0.7)
    
    plt.xlabel('Nombre de Threads', fontsize=12)
    plt.ylabel('Efficacité (%)', fontsize=12)
    plt.title('Efficacité Parallèle en Fonction du Nombre de Threads', fontsize=14, fontweight='bold')
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.ylim(0, 110)
    
    # Ajouter les valeurs
    for threads, eff in zip(thread_counts, efficiencies):
        plt.text(threads, eff + 2, f'{eff:.1f}%', 
                ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/efficiency_analysis.png', dpi=300)
    print(f"  ✅ Graphique sauvegardé : {output_dir}/efficiency_analysis.png")
    plt.close()


def plot_detailed_comparison(results, output_dir='graphs'):
    """
    Graphique 4 : Comparaison détaillée (subplots).
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    mono_time = results['mono_thread']['avg_time']
    thread_counts = [r['num_threads'] for r in results['multi_thread']]
    multi_times = [r['avg_time'] for r in results['multi_thread']]
    speedups = [r['speedup'] for r in results['multi_thread']]
    efficiencies = [r['efficiency'] * 100 for r in results['multi_thread']]
    
    # Subplot 1 : Temps d'exécution
    axes[0, 0].bar(['Mono'] + [f'{t}T' for t in thread_counts], 
                   [mono_time] + multi_times, 
                   color=['red'] + ['green'] * len(thread_counts), alpha=0.7)
    axes[0, 0].set_ylabel('Temps (s)')
    axes[0, 0].set_title('Temps d\'Exécution')
    axes[0, 0].grid(axis='y', alpha=0.3)
    
    # Subplot 2 : Speedup
    axes[0, 1].plot(thread_counts, speedups, 'o-', linewidth=2, markersize=8, color='blue')
    axes[0, 1].plot(thread_counts, thread_counts, '--', linewidth=2, color='gray', alpha=0.7)
    axes[0, 1].set_xlabel('Threads')
    axes[0, 1].set_ylabel('Speedup (×)')
    axes[0, 1].set_title('Speedup vs Threads')
    axes[0, 1].grid(True, alpha=0.3)
    axes[0, 1].legend(['Réel', 'Idéal'])
    
    # Subplot 3 : Efficacité
    axes[1, 0].plot(thread_counts, efficiencies, 'o-', linewidth=2, markersize=8, color='purple')
    axes[1, 0].axhline(y=100, color='gray', linestyle='--', linewidth=2, alpha=0.7)
    axes[1, 0].set_xlabel('Threads')
    axes[1, 0].set_ylabel('Efficacité (%)')
    axes[1, 0].set_title('Efficacité Parallèle')
    axes[1, 0].grid(True, alpha=0.3)
    axes[1, 0].set_ylim(0, 110)
    
    # Subplot 4 : Throughput
    mono_throughput = results['iterations'] / mono_time
    multi_throughputs = [results['iterations'] / t for t in multi_times]
    
    axes[1, 1].bar(['Mono'] + [f'{t}T' for t in thread_counts], 
                   [mono_throughput] + multi_throughputs, 
                   color=['red'] + ['green'] * len(thread_counts), alpha=0.7)
    axes[1, 1].set_ylabel('Itérations/seconde')
    axes[1, 1].set_title('Throughput (Débit)')
    axes[1, 1].grid(axis='y', alpha=0.3)
    axes[1, 1].ticklabel_format(style='scientific', axis='y', scilimits=(0,0))
    
    plt.suptitle('Analyse Complète : Mono-Thread vs Multi-Thread', 
                 fontsize=16, fontweight='bold', y=0.995)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/detailed_comparison.png', dpi=300)
    print(f"  ✅ Graphique sauvegardé : {output_dir}/detailed_comparison.png")
    plt.close()


def generate_all_graphs(results_file='results/benchmark_results.json', output_dir='graphs'):
    """
    Génère tous les graphiques.
    """
    print("\n📊 Génération des graphiques...")
    
    # Charger les résultats
    results = load_results(results_file)
    
    # Créer le dossier de sortie
    os.makedirs(output_dir, exist_ok=True)
    
    # Générer les graphiques
    plot_execution_time_comparison(results, output_dir)
    plot_speedup(results, output_dir)
    plot_efficiency(results, output_dir)
    plot_detailed_comparison(results, output_dir)
    
    print(f"\n✅ Tous les graphiques ont été générés dans '{output_dir}/'")


def main():
    """Fonction principale."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Générer les graphiques de comparaison')
    parser.add_argument('--input', type=str, default='results/benchmark_results.json',
                        help='Fichier JSON des résultats')
    parser.add_argument('--output', type=str, default='graphs',
                        help='Dossier de sortie pour les graphiques')
    args = parser.parse_args()
    
    generate_all_graphs(args.input, args.output)


if __name__ == "__main__":
    main()
