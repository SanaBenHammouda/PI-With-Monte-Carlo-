# Document de Conception - Système de Gestion des Paramètres WMIC

## Vue d'ensemble

Ce document décrit la conception d'un système de gestion des paramètres WMIC qui détecte l'installation de WMIC sur un serveur Windows, gère les paramètres de configuration, et documente les opérations dans un journal CR. Le système sera implémenté en Python pour la portabilité et la facilité de maintenance.

## Architecture

### Architecture Globale

```
┌─────────────────────────────────────────────────────────┐
│                    Système Principal                     │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │         Configuration Manager                      │ │
│  │  - Lecture/Écriture config                        │ │
│  │  - Validation paramètres                          │ │
│  └────────────────┬───────────────────────────────────┘ │
│                   │                                      │
│                   v                                      │
│  ┌────────────────────────────────────────────────────┐ │
│  │         WMIC Detector                              │ │
│  │  - Détection installation                         │ │
│  │  - Vérification version Windows                   │ │
│  └────────────────┬───────────────────────────────────┘ │
│                   │                                      │
│                   v                                      │
│  ┌────────────────────────────────────────────────────┐ │
│  │         Error Handler                              │ │
│  │  - Gestion erreurs                                │ │
│  │  - Messages d'erreur                              │ │
│  └────────────────┬───────────────────────────────────┘ │
│                   │                                      │
│                   v                                      │
│  ┌────────────────────────────────────────────────────┐ │
│  │         CR Journal Writer                          │ │
│  │  - Écriture journal                               │ │
│  │  - Documentation changements                      │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │         Logger                                     │ │
│  │  - Logs système                                   │ │
│  │  - Niveaux de log                                 │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## Composants et Interfaces

### 1. Classe WMICDetector

**Responsabilité**: Détecter la présence et la disponibilité de WMIC sur le système.

**Méthodes**:
- `is_wmic_installed() -> bool` - Vérifie si WMIC est installé
- `get_windows_version() -> str` - Retourne la version de Windows
- `is_wmic_deprecated() -> bool` - Vérifie si WMIC est déprécié
- `get_wmic_path() -> Optional[str]` - Retourne le chemin vers WMIC

**Algorithme de détection**:
```
1. Vérifier si wmic.exe existe dans System32
2. Tenter d'exécuter "wmic /?" pour confirmer
3. Vérifier la version de Windows
4. Déterminer si WMIC est déprécié
5. Retourner le statut
```

### 2. Classe ConfigurationManager

**Responsabilité**: Gérer les paramètres de configuration du système.

**Attributs**:
- `parameter_value: Optional[str]` - Valeur du paramètre ('Y', 'N', None)
- `config_file_path: str` - Chemin vers le fichier de configuration
- `is_valid: bool` - Indique si la configuration est valide

**Méthodes**:
- `load_configuration() -> None` - Charge la configuration depuis le fichier
- `save_configuration() -> None` - Sauvegarde la configuration
- `validate_parameter(value: str) -> bool` - Valide une valeur de paramètre
- `get_parameter() -> Optional[str]` - Retourne la valeur du paramètre
- `set_parameter(value: Optional[str]) -> None` - Définit le paramètre
- `reset_to_default() -> None` - Réinitialise à la configuration par défaut

### 3. Classe ErrorHandler

**Responsabilité**: Gérer les erreurs et générer des messages appropriés.

**Méthodes**:
- `handle_wmic_not_installed(parameter: str) -> WMICError` - Gère l'erreur WMIC non installé
- `should_raise_error(parameter: Optional[str], wmic_installed: bool) -> bool` - Détermine si une erreur doit être levée
- `get_error_message(error_type: str) -> str` - Génère un message d'erreur
- `log_error(error: Exception) -> None` - Log une erreur

**Logique de gestion d'erreur**:
```
SI paramètre == 'Y' ET WMIC non installé:
    Lever WMICNotInstalledError
SINON SI paramètre == 'N' OU paramètre == None:
    Ne pas lever d'erreur
    Logger l'information
```

### 4. Classe CRJournalWriter

**Responsabilité**: Écrire et gérer le journal CR.

**Attributs**:
- `journal_file_path: str` - Chemin vers le fichier journal
- `entries: List[CREntry]` - Liste des entrées

**Méthodes**:
- `add_entry(entry: CREntry) -> None` - Ajoute une entrée au journal
- `write_wmic_status(parameter: str, wmic_installed: bool, error: Optional[str]) -> None` - Documente le statut WMIC
- `get_last_entry() -> Optional[CREntry]` - Retourne la dernière entrée
- `format_entry(entry: CREntry) -> str` - Formate une entrée pour l'affichage

### 5. Classe CREntry

**Responsabilité**: Représenter une entrée dans le journal CR.

**Attributs**:
- `timestamp: datetime` - Date et heure de l'entrée
- `parameter_value: Optional[str]` - Valeur du paramètre
- `wmic_installed: bool` - Statut d'installation WMIC
- `error_occurred: bool` - Indique si une erreur s'est produite
- `description: str` - Description de l'entrée
- `action_taken: str` - Action effectuée

### 6. Classe SystemStatus

**Responsabilité**: Fournir un rapport de statut du système.

**Attributs**:
- `wmic_installed: bool`
- `parameter_value: Optional[str]`
- `last_error: Optional[str]`
- `windows_version: str`
- `wmic_deprecated: bool`

**Méthodes**:
- `generate_report() -> str` - Génère un rapport de statut
- `is_healthy() -> bool` - Indique si le système est en bon état

### 7. Module Logger

**Responsabilité**: Gérer les logs du système.

**Fonctions**:
- `setup_logger(log_level: str, log_file: str) -> logging.Logger` - Configure le logger
- `log_info(message: str) -> None`
- `log_warning(message: str) -> None`
- `log_error(message: str, exception: Optional[Exception]) -> None`
- `log_debug(message: str) -> None`

## Modèles de Données

### Configuration File (JSON)
```json
{
    "wmic_parameter": "N",
    "last_updated": "2026-01-19T10:30:00",
    "version": "1.0"
}
```

### CR Journal Entry (JSON)
```json
{
    "timestamp": "2026-01-19T10:30:00",
    "parameter_value": "Y",
    "wmic_installed": false,
    "error_occurred": true,
    "description": "WMIC parameter set to Y but WMIC is not installed on the server",
    "action_taken": "Generated 'not installed' error",
    "notes": "When parameter is Y: results in 'not installed' error. When N or undefined: no error occurs."
}
```

### System Status Report
```
=== WMIC System Status Report ===
Timestamp: 2026-01-19 10:30:00
Windows Version: Windows Server 2019
WMIC Installed: No
WMIC Deprecated: No
Parameter Value: N
Last Error: None
System Health: OK
================================
```

## Propriétés de Correction

*Une propriété est une caractéristique ou un comportement qui doit être vrai pour toutes les exécutions valides d'un système.*

### Propriété 1: Détection cohérente de WMIC

*Pour tout* système Windows, la détection de WMIC doit retourner un résultat cohérent (installé ou non installé) et ce résultat doit correspondre à la présence réelle de wmic.exe.

**Valide: Exigences 1.1, 1.2, 1.3**

---

### Propriété 2: Validation des paramètres

*Pour toute* valeur de paramètre fournie, si la valeur n'est pas 'Y', 'N', ou None, alors la validation doit échouer.

**Valide: Exigences 2.5, 6.1, 6.2**

---

### Propriété 3: Génération d'erreur conditionnelle

*Pour tout* état du système, une erreur "not installed" doit être générée si et seulement si le paramètre est 'Y' ET WMIC n'est pas installé.

**Valide: Exigences 3.1, 3.2, 3.3**

---

### Propriété 4: Comportement par défaut sûr

*Pour tout* système où le paramètre est undefined (None), le comportement doit être identique au paramètre 'N' (pas d'erreur).

**Valide: Exigences 5.1, 5.2, 5.3**

---

### Propriété 5: Persistance de configuration

*Pour toute* configuration sauvegardée puis rechargée, les valeurs doivent être identiques (round-trip).

**Valide: Exigences 10.1, 10.2, 10.3**

---

### Propriété 6: Complétude des entrées CR

*Pour toute* entrée de journal CR créée, elle doit contenir tous les champs requis: timestamp, parameter_value, wmic_installed, description.

**Valide: Exigences 4.1, 4.2, 4.3, 4.4**

---

### Propriété 7: Logs horodatés

*Pour toute* entrée de log créée, elle doit contenir un timestamp valide.

**Valide: Exigences 7.5**

---

### Propriété 8: Messages d'erreur actionnables

*Pour toute* erreur générée, le message d'erreur doit contenir des informations sur la cause et suggérer une action corrective.

**Valide: Exigences 3.5, 6.3, 6.4**

## Gestion des Erreurs

### Types d'Erreurs

1. **WMICNotInstalledError**
   - Levée quand: paramètre='Y' et WMIC non installé
   - Message: "WMIC is not installed on this server. Please install WMIC or set the parameter to 'N'."
   - Action: Logger l'erreur, créer entrée CR, arrêter l'opération

2. **InvalidParameterError**
   - Levée quand: valeur de paramètre invalide
   - Message: "Invalid parameter value '{value}'. Allowed values are: 'Y', 'N', or undefined."
   - Action: Rejeter la configuration, suggérer valeurs valides

3. **ConfigurationFileError**
   - Levée quand: fichier de configuration corrompu
   - Message: "Configuration file is corrupted. Resetting to default."
   - Action: Réinitialiser à la configuration par défaut

4. **WindowsVersionError**
   - Levée quand: version Windows non supportée
   - Message: "Windows version {version} is not supported. Minimum: Windows Server 2012 R2."
   - Action: Logger l'avertissement, continuer avec fonctionnalités limitées

### Stratégie de Gestion

```python
try:
    # Charger configuration
    config = load_configuration()
    
    # Détecter WMIC
    wmic_installed = detect_wmic()
    
    # Vérifier si erreur doit être levée
    if config.parameter == 'Y' and not wmic_installed:
        raise WMICNotInstalledError()
    
    # Créer entrée CR
    create_cr_entry(config.parameter, wmic_installed, error=None)
    
except WMICNotInstalledError as e:
    log_error(e)
    create_cr_entry(config.parameter, wmic_installed, error=str(e))
    raise
    
except Exception as e:
    log_error(e)
    handle_unexpected_error(e)
```

## Stratégie de Test

### Tests Unitaires

**ConfigurationManager**:
- Test de chargement de configuration valide
- Test de validation de paramètres ('Y', 'N', None, invalide)
- Test de sauvegarde et rechargement (round-trip)
- Test de réinitialisation par défaut

**WMICDetector**:
- Test de détection sur système avec WMIC
- Test de détection sur système sans WMIC
- Test de détection de version Windows
- Test de détection de dépréciation WMIC

**ErrorHandler**:
- Test de génération d'erreur (paramètre='Y', WMIC absent)
- Test de non-génération d'erreur (paramètre='N', WMIC absent)
- Test de non-génération d'erreur (paramètre=None, WMIC absent)
- Test de messages d'erreur

**CRJournalWriter**:
- Test d'ajout d'entrée
- Test de formatage d'entrée
- Test de récupération de dernière entrée

### Tests de Propriétés (Hypothesis)

**Propriété 2: Validation des paramètres**
```python
@given(parameter=st.text())
def test_parameter_validation(parameter):
    config = ConfigurationManager()
    is_valid = config.validate_parameter(parameter)
    
    if parameter in ['Y', 'N', None]:
        assert is_valid
    else:
        assert not is_valid
```

**Propriété 3: Génération d'erreur conditionnelle**
```python
@given(
    parameter=st.sampled_from(['Y', 'N', None]),
    wmic_installed=st.booleans()
)
def test_error_generation(parameter, wmic_installed):
    handler = ErrorHandler()
    should_error = handler.should_raise_error(parameter, wmic_installed)
    
    assert should_error == (parameter == 'Y' and not wmic_installed)
```

**Propriété 5: Persistance de configuration**
```python
@given(parameter=st.sampled_from(['Y', 'N', None]))
def test_configuration_persistence(parameter):
    config = ConfigurationManager()
    config.set_parameter(parameter)
    config.save_configuration()
    
    config2 = ConfigurationManager()
    config2.load_configuration()
    
    assert config2.get_parameter() == parameter
```

### Tests d'Intégration

1. **Scénario complet avec paramètre='Y' et WMIC absent**
   - Vérifier que l'erreur est levée
   - Vérifier que l'entrée CR est créée
   - Vérifier que les logs sont corrects

2. **Scénario complet avec paramètre='N' et WMIC absent**
   - Vérifier qu'aucune erreur n'est levée
   - Vérifier que l'entrée CR est créée
   - Vérifier le comportement normal

3. **Scénario complet avec paramètre=undefined et WMIC absent**
   - Vérifier le comportement par défaut
   - Vérifier qu'aucune erreur n'est levée

## Diagrammes de Séquence

### Séquence: Vérification avec paramètre='Y'

```
User -> System: set_parameter('Y')
System -> ConfigManager: validate_parameter('Y')
ConfigManager -> System: valid
System -> WMICDetector: is_wmic_installed()
WMICDetector -> System: False
System -> ErrorHandler: should_raise_error('Y', False)
ErrorHandler -> System: True
System -> CRJournal: write_entry('Y', False, error)
System -> Logger: log_error()
System -> User: WMICNotInstalledError
```

### Séquence: Vérification avec paramètre='N'

```
User -> System: set_parameter('N')
System -> ConfigManager: validate_parameter('N')
ConfigManager -> System: valid
System -> WMICDetector: is_wmic_installed()
WMICDetector -> System: False
System -> ErrorHandler: should_raise_error('N', False)
ErrorHandler -> System: False
System -> CRJournal: write_entry('N', False, no_error)
System -> Logger: log_info()
System -> User: Success
```

## Considérations d'Implémentation

### Choix de Python

- Portabilité entre versions Windows
- Bibliothèques standard pour détection système
- Facilité de gestion des fichiers JSON
- Support natif du logging

### Détection de WMIC

```python
import os
import subprocess
import platform

def is_wmic_installed():
    # Méthode 1: Vérifier le fichier
    wmic_path = os.path.join(os.environ['SystemRoot'], 'System32', 'wmic.exe')
    if not os.path.exists(wmic_path):
        return False
    
    # Méthode 2: Tenter d'exécuter
    try:
        result = subprocess.run(['wmic', '/?'], 
                              capture_output=True, 
                              timeout=5)
        return result.returncode == 0
    except:
        return False
```

### Gestion de la Dépréciation WMIC

WMIC est déprécié depuis Windows 10 21H1. Le système doit:
- Détecter la version de Windows
- Avertir si WMIC est déprécié
- Suggérer des alternatives (PowerShell, WMI via Python)

## Conclusion

Cette conception fournit un système robuste pour gérer les paramètres WMIC avec:
- Détection fiable de l'installation WMIC
- Gestion appropriée des erreurs selon la configuration
- Documentation complète dans le journal CR
- Comportement par défaut sûr
- Logs complets pour le débogage
