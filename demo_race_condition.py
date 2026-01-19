"""
Démonstration des Race Conditions (Conditions de Course)

Ce script montre :
1. Un exemple BUGGÉ avec race condition
2. La solution CORRECTE avec synchronisation
3. La différence de résultats
"""

import threading
import time


# ============================================================================
# EXEMPLE 1 : RACE CONDITION (BUGGÉ)
# ============================================================================

counter_buggy = 0

def increment_buggy(num_iterations):
    """
    Version BUGGÉE : Incrémente un compteur partagé sans synchronisation.
    
    Problème : Plusieurs threads lisent et écrivent counter_buggy en même temps,
    causant des pertes de mises à jour.
    """
    global counter_buggy
    for _ in range(num_iterations):
        # DANGER : Cette opération n'est PAS atomique !
        # Elle se décompose en : lire, incrémenter, écrire
        counter_buggy += 1


def demo_race_condition():
    """Démontre le problème de race condition."""
    global counter_buggy
    counter_buggy = 0
    
    num_threads = 4
    iterations_per_thread = 100_000
    expected_result = num_threads * iterations_per_thread
    
    print("=" * 70)
    print("DÉMONSTRATION : RACE CONDITION (BUGGÉ)")
    print("=" * 70)
    print(f"Nombre de threads        : {num_threads}")
    print(f"Incréments par thread    : {iterations_per_thread:,}")
    print(f"Résultat attendu         : {expected_result:,}")
    print("\nExécution...")
    
    # Créer et démarrer les threads
    threads = []
    start_time = time.time()
    
    for _ in range(num_threads):
        t = threading.Thread(target=increment_buggy, args=(iterations_per_thread,))
        threads.append(t)
        t.start()
    
    # Attendre la fin
    for t in threads:
        t.join()
    
    end_time = time.time()
    
    print(f"\n{'=' * 70}")
    print("RÉSULTATS")
    print("=" * 70)
    print(f"Résultat obtenu          : {counter_buggy:,}")
    print(f"Résultat attendu         : {expected_result:,}")
    print(f"Différence (pertes)      : {expected_result - counter_buggy:,}")
    print(f"Pourcentage de pertes    : {(1 - counter_buggy/expected_result) * 100:.2f}%")
    print(f"Temps d'exécution        : {end_time - start_time:.4f}s")
    
    if counter_buggy != expected_result:
        print("\n⚠️  RACE CONDITION DÉTECTÉE !")
        print("   Des incréments ont été perdus à cause d'accès concurrents non synchronisés.")
    else:
        print("\n✅ Pas de race condition détectée (rare, mais possible)")
    
    print("=" * 70)


# ============================================================================
# EXEMPLE 2 : SOLUTION CORRECTE (AVEC LOCK)
# ============================================================================

counter_safe = 0
counter_lock = threading.Lock()

def increment_safe(num_iterations):
    """
    Version CORRECTE : Incrémente un compteur partagé avec synchronisation.
    
    Solution : Utilise un Lock pour garantir qu'un seul thread accède
    au compteur à la fois.
    """
    global counter_safe
    for _ in range(num_iterations):
        # CORRECT : Le lock garantit l'atomicité
        with counter_lock:
            counter_safe += 1


def demo_with_lock():
    """Démontre la solution avec Lock."""
    global counter_safe
    counter_safe = 0
    
    num_threads = 4
    iterations_per_thread = 100_000
    expected_result = num_threads * iterations_per_thread
    
    print("\n" + "=" * 70)
    print("DÉMONSTRATION : SOLUTION AVEC LOCK (CORRECT)")
    print("=" * 70)
    print(f"Nombre de threads        : {num_threads}")
    print(f"Incréments par thread    : {iterations_per_thread:,}")
    print(f"Résultat attendu         : {expected_result:,}")
    print("\nExécution...")
    
    # Créer et démarrer les threads
    threads = []
    start_time = time.time()
    
    for _ in range(num_threads):
        t = threading.Thread(target=increment_safe, args=(iterations_per_thread,))
        threads.append(t)
        t.start()
    
    # Attendre la fin
    for t in threads:
        t.join()
    
    end_time = time.time()
    
    print(f"\n{'=' * 70}")
    print("RÉSULTATS")
    print("=" * 70)
    print(f"Résultat obtenu          : {counter_safe:,}")
    print(f"Résultat attendu         : {expected_result:,}")
    print(f"Différence               : {expected_result - counter_safe:,}")
    print(f"Temps d'exécution        : {end_time - start_time:.4f}s")
    
    if counter_safe == expected_result:
        print("\n✅ CORRECT ! Aucune perte grâce au Lock.")
    else:
        print("\n⚠️  Erreur inattendue")
    
    print("=" * 70)


# ============================================================================
# EXEMPLE 3 : COMPARAISON VISUELLE
# ============================================================================

def visual_comparison():
    """Comparaison visuelle des deux approches."""
    print("\n" + "=" * 70)
    print("COMPARAISON VISUELLE DU CODE")
    print("=" * 70)
    
    print("\n❌ VERSION BUGGÉE (Race Condition):")
    print("-" * 70)
    print("""
counter = 0

def increment_buggy():
    global counter
    for _ in range(100000):
        counter += 1  # ⚠️ NON THREAD-SAFE !

# Plusieurs threads exécutent increment_buggy() en parallèle
# → Pertes de mises à jour !
    """)
    
    print("\n✅ VERSION CORRECTE (Avec Lock):")
    print("-" * 70)
    print("""
counter = 0
lock = threading.Lock()

def increment_safe():
    global counter
    for _ in range(100000):
        with lock:  # ✅ THREAD-SAFE
            counter += 1

# Plusieurs threads exécutent increment_safe() en parallèle
# → Aucune perte, résultat correct !
    """)
    
    print("=" * 70)
    print("\n💡 LEÇON IMPORTANTE :")
    print("   - Les opérations sur variables partagées doivent être protégées")
    print("   - Utilisez Lock, Queue, ou autres primitives de synchronisation")
    print("   - Testez toujours avec plusieurs threads pour détecter les bugs")
    print("=" * 70)


def main():
    """Fonction principale."""
    print("\n" + "🔬" * 35)
    print("DÉMONSTRATION : RACE CONDITIONS ET SYNCHRONISATION")
    print("🔬" * 35)
    
    # Démo 1 : Race condition
    demo_race_condition()
    
    # Démo 2 : Solution avec Lock
    demo_with_lock()
    
    # Comparaison visuelle
    visual_comparison()
    
    print("\n" + "=" * 70)
    print("FIN DE LA DÉMONSTRATION")
    print("=" * 70)
    print("\nPour en savoir plus sur la synchronisation en Python :")
    print("  - threading.Lock : Verrou basique")
    print("  - threading.RLock : Verrou réentrant")
    print("  - threading.Semaphore : Limite le nombre d'accès concurrents")
    print("  - queue.Queue : File thread-safe")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
