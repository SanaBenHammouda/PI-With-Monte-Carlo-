# Système de Gestion des Paramètres WMIC

## Description

Ce système gère les paramètres WMIC (Windows Management Instrumentation Command-line) sur les serveurs Windows. Il détecte automatiquement si WMIC est installé, gère les paramètres de configuration, génère des erreurs appropriées selon la configuration, et documente toutes les opérations dans un journal CR (Change Request).

## Contexte

Suite à un problème identifié où:
- **Paramètre = 'Y'**: Résulte en une erreur "not installed" si WMIC n'est pas installé
- **Paramètre = 'N' ou undefined**: Aucune erreur ne se produit

Ce système fournit une gestion robuste de ces scénarios avec documentation complète.

## Fonctionnalités

✅ Détection automatique de l'installation WMIC  
✅ Gestion des paramètres de configuration ('Y', 'N', undefined)  
✅ Génération d'erreurs conditionnelles selon la configuration  
✅ Journal CR complet pour documenter les changements  
✅ Logs détaillés à plusieurs niveaux  
✅ Rapports de statut système  
✅ Support de multiples versions de Windows  
✅ Détection de la dépréciation de WMIC  
✅ Configuration persistante  
✅ Interface en ligne de commande  

## Installation

```bash
# Installer les dépendances
pip install -r requirements.txt
```

## Utilisation

### Vérifier le statut WMIC

```bash
python src/main.py check
```

### Définir le paramètre

```bash
# Activer WMIC (génère une erreur si non installé)
python src/main.py set-parameter --value Y

# Désactiver WMIC (pas d'erreur)
python src/main.py set-parameter --value N

# Utiliser la valeur par défaut
python src/main.py set-parameter --value default
```

### Afficher le rapport de statut

```bash
python src/main.py status
```

### Afficher le journal CR

```bash
python src/main.py journal
```

### Réinitialiser la configuration

```bash
python src/main.py reset
```

## Scénarios d'Utilisation

### Scénario 1: WMIC non installé, paramètre='Y'

```bash
$ python src/main.py set-parameter --value Y
$ python src/main.py check
ERROR: WMIC is not installed on this server.
Please install WMIC or set the parameter to 'N'.
```

**Résultat**: Une erreur est générée et documentée dans le journal CR.

### Scénario 2: WMIC non installé, paramètre='N'

```bash
$ python src/main.py set-parameter --value N
$ python src/main.py check
INFO: WMIC parameter set to 'N'. WMIC operations are disabled.
```

**Résultat**: Aucune erreur, le système fonctionne normalement.

### Scénario 3: WMIC non installé, paramètre=undefined

```bash
$ python src/main.py reset
$ python src/main.py check
INFO: WMIC parameter is undefined (default behavior: disabled).
```

**Résultat**: Aucune erreur, comportement par défaut sûr.

## Structure du Projet

```
wmic-system/
├── src/
│   ├── wmic_detector.py         # Détection de WMIC
│   ├── config_manager.py        # Gestion de configuration
│   ├── error_handler.py         # Gestion des erreurs
│   ├── cr_journal.py            # Journal CR
│   ├── system_status.py         # Rapports de statut
│   ├── logger_setup.py          # Configuration des logs
│   ├── wmic_system.py           # Classe principale
│   ├── exceptions.py            # Exceptions personnalisées
│   └── main.py                  # Interface CLI
├── tests/
│   ├── test_wmic_detector.py
│   ├── test_config_manager.py
│   ├── test_error_handler.py
│   ├── test_cr_journal.py
│   ├── test_system_status.py
│   └── test_integration.py
├── config/
│   └── config.json              # Configuration système
├── logs/
│   └── wmic_system.log          # Logs système
├── journal/
│   └── cr_journal.json          # Journal CR
├── requirements.txt
└── README.md
```

## Configuration

Le fichier `config/config.json` contient:

```json
{
    "wmic_parameter": "N",
    "last_updated": "2026-01-19T10:30:00",
    "version": "1.0"
}
```

### Valeurs de Paramètre

- **'Y'**: Active WMIC (génère une erreur si non installé)
- **'N'**: Désactive WMIC (pas d'erreur)
- **undefined/null**: Comportement par défaut (équivalent à 'N')

## Journal CR

Chaque opération est documentée dans le journal CR avec:

- Timestamp
- Valeur du paramètre
- Statut d'installation WMIC
- Erreur éventuelle
- Description de l'action
- Notes explicatives

Exemple d'entrée:

```json
{
    "timestamp": "2026-01-19T10:30:00",
    "parameter_value": "Y",
    "wmic_installed": false,
    "error_occurred": true,
    "description": "WMIC parameter set to Y but WMIC is not installed",
    "action_taken": "Generated 'not installed' error",
    "notes": "When parameter is Y: error occurs. When N or undefined: no error."
}
```

## Logs

Les logs sont écrits dans `logs/wmic_system.log` avec plusieurs niveaux:

- **DEBUG**: Informations détaillées pour le débogage
- **INFO**: Informations générales sur les opérations
- **WARNING**: Avertissements (ex: WMIC déprécié)
- **ERROR**: Erreurs nécessitant attention

### Configuration du Niveau de Log

```bash
python src/main.py check --log-level DEBUG
```

## Compatibilité

- Windows Server 2012 R2 et versions ultérieures
- Windows 10/11
- Python 3.7+

## Notes sur la Dépréciation de WMIC

WMIC est déprécié depuis Windows 10 21H1. Le système:
- Détecte automatiquement si WMIC est déprécié
- Affiche des avertissements appropriés
- Suggère des alternatives (PowerShell, WMI via Python)

## Tests

```bash
# Tous les tests
pytest tests/ -v

# Tests unitaires uniquement
pytest tests/ -v -k "not property"

# Tests de propriétés uniquement
pytest tests/ -v -k "property"
```

## Dépannage

### Erreur: "WMIC is not installed"

**Cause**: Le paramètre est défini à 'Y' mais WMIC n'est pas installé.

**Solutions**:
1. Installer WMIC sur le serveur
2. Définir le paramètre à 'N': `python src/main.py set-parameter --value N`

### Erreur: "Invalid parameter value"

**Cause**: Valeur de paramètre invalide fournie.

**Solution**: Utiliser uniquement 'Y', 'N', ou 'default'.

### Erreur: "Configuration file is corrupted"

**Cause**: Le fichier de configuration est corrompu.

**Solution**: Réinitialiser la configuration: `python src/main.py reset`

## FAQ

**Q: Quelle est la valeur par défaut du paramètre?**  
R: Par défaut, le paramètre est undefined (None), ce qui équivaut à 'N' (WMIC désactivé).

**Q: Que se passe-t-il si WMIC est installé mais déprécié?**  
R: Le système fonctionne normalement mais affiche un avertissement suggérant des alternatives.

**Q: Puis-je utiliser ce système sur Windows 11?**  
R: Oui, le système est compatible avec Windows 11, mais notez que WMIC est déprécié.

**Q: Comment voir l'historique complet des changements?**  
R: Utilisez `python src/main.py journal` pour afficher toutes les entrées du journal CR.

## Auteur

Système créé pour gérer les paramètres WMIC et documenter les changements dans un journal CR.

## Licence

Ce projet est à usage interne.
