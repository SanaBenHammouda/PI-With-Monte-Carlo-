"""
Module pour gérer le journal CR (Change Request).
"""
import json
import os
from datetime import datetime
from typing import List, Optional, Dict


class CREntry:
    """
    Représente une entrée dans le journal CR.
    """
    
    def __init__(
        self,
        parameter_value: Optional[str],
        wmic_installed: bool,
        error_occurred: bool,
        description: str,
        action_taken: str,
        notes: str = ""
    ):
        """
        Initialise une entrée CR.
        
        Args:
            parameter_value: Valeur du paramètre
            wmic_installed: Statut d'installation WMIC
            error_occurred: Indique si une erreur s'est produite
            description: Description de l'opération
            action_taken: Action effectuée
            notes: Notes additionnelles
        """
        self.timestamp = datetime.now().isoformat()
        self.parameter_value = parameter_value
        self.wmic_installed = wmic_installed
        self.error_occurred = error_occurred
        self.description = description
        self.action_taken = action_taken
        self.notes = notes
    
    def to_dict(self) -> Dict:
        """
        Convertit l'entrée en dictionnaire pour sérialisation.
        
        Returns:
            Dictionnaire représentant l'entrée
        """
        return {
            'timestamp': self.timestamp,
            'parameter_value': self.parameter_value,
            'wmic_installed': self.wmic_installed,
            'error_occurred': self.error_occurred,
            'description': self.description,
            'action_taken': self.action_taken,
            'notes': self.notes
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'CREntry':
        """
        Crée une entrée depuis un dictionnaire.
        
        Args:
            data: Dictionnaire contenant les données
            
        Returns:
            Instance de CREntry
        """
        entry = cls(
            parameter_value=data.get('parameter_value'),
            wmic_installed=data.get('wmic_installed', False),
            error_occurred=data.get('error_occurred', False),
            description=data.get('description', ''),
            action_taken=data.get('action_taken', ''),
            notes=data.get('notes', '')
        )
        entry.timestamp = data.get('timestamp', datetime.now().isoformat())
        return entry
    
    def __str__(self) -> str:
        """Représentation textuelle de l'entrée."""
        param_display = self.parameter_value if self.parameter_value else 'undefined'
        error_status = 'ERROR' if self.error_occurred else 'OK'
        
        lines = [
            "=" * 70,
            f"CR Entry - {self.timestamp}",
            "=" * 70,
            f"Parameter Value:    {param_display}",
            f"WMIC Installed:     {self.wmic_installed}",
            f"Status:             {error_status}",
            f"Description:        {self.description}",
            f"Action Taken:       {self.action_taken}",
        ]
        
        if self.notes:
            lines.append(f"Notes:              {self.notes}")
        
        lines.append("=" * 70)
        return "\n".join(lines)


class CRJournalWriter:
    """
    Gère l'écriture et la lecture du journal CR.
    """
    
    def __init__(self, journal_file_path: str = 'journal/cr_journal.json'):
        """
        Initialise le gestionnaire de journal CR.
        
        Args:
            journal_file_path: Chemin vers le fichier journal
        """
        self.journal_file_path = journal_file_path
        self.entries: List[CREntry] = []
        self._load_journal()
    
    def _load_journal(self) -> None:
        """Charge le journal depuis le fichier."""
        if os.path.exists(self.journal_file_path):
            try:
                with open(self.journal_file_path, 'r') as f:
                    data = json.load(f)
                    self.entries = [CREntry.from_dict(entry) for entry in data]
            except (json.JSONDecodeError, KeyError):
                # Fichier corrompu, commencer avec un journal vide
                self.entries = []
    
    def _save_journal(self) -> None:
        """Sauvegarde le journal dans le fichier."""
        # Créer le répertoire si nécessaire
        os.makedirs(os.path.dirname(self.journal_file_path), exist_ok=True)
        
        # Sauvegarder toutes les entrées
        data = [entry.to_dict() for entry in self.entries]
        with open(self.journal_file_path, 'w') as f:
            json.dump(data, f, indent=4)
    
    def add_entry(self, entry: CREntry) -> None:
        """
        Ajoute une entrée au journal.
        
        Args:
            entry: Entrée à ajouter
        """
        self.entries.append(entry)
        self._save_journal()
    
    def write_wmic_status(
        self,
        parameter: Optional[str],
        wmic_installed: bool,
        error: Optional[str] = None
    ) -> None:
        """
        Documente le statut WMIC dans le journal.
        
        Args:
            parameter: Valeur du paramètre
            wmic_installed: Statut d'installation WMIC
            error: Message d'erreur éventuel
        """
        # Déterminer la description
        param_display = parameter if parameter else 'undefined'
        if error:
            description = f"WMIC parameter set to '{param_display}' but WMIC is not installed on the server"
            action_taken = "Generated 'not installed' error"
        else:
            if parameter == 'Y' and wmic_installed:
                description = f"WMIC parameter set to '{param_display}' and WMIC is installed"
                action_taken = "WMIC operations enabled"
            elif parameter == 'N' or parameter is None:
                description = f"WMIC parameter set to '{param_display}'"
                action_taken = "WMIC operations disabled (no error)"
            else:
                description = f"WMIC status checked with parameter '{param_display}'"
                action_taken = "Status check completed"
        
        # Notes explicatives
        notes = (
            "When parameter is set to Y: results in 'not installed' error if WMIC is absent. "
            "When set to N or undefined (default): no error occurs."
        )
        
        # Créer et ajouter l'entrée
        entry = CREntry(
            parameter_value=parameter,
            wmic_installed=wmic_installed,
            error_occurred=error is not None,
            description=description,
            action_taken=action_taken,
            notes=notes
        )
        
        self.add_entry(entry)
    
    def get_last_entry(self) -> Optional[CREntry]:
        """
        Retourne la dernière entrée du journal.
        
        Returns:
            Dernière entrée ou None si le journal est vide
        """
        if self.entries:
            return self.entries[-1]
        return None
    
    def get_all_entries(self) -> List[CREntry]:
        """
        Retourne toutes les entrées du journal.
        
        Returns:
            Liste de toutes les entrées
        """
        return self.entries.copy()
    
    def format_entry(self, entry: CREntry) -> str:
        """
        Formate une entrée pour l'affichage.
        
        Args:
            entry: Entrée à formater
            
        Returns:
            Chaîne formatée
        """
        return str(entry)
    
    def format_all_entries(self) -> str:
        """
        Formate toutes les entrées pour l'affichage.
        
        Returns:
            Chaîne contenant toutes les entrées formatées
        """
        if not self.entries:
            return "No CR journal entries found."
        
        lines = ["\n" + "=" * 70]
        lines.append("CR JOURNAL - ALL ENTRIES")
        lines.append("=" * 70 + "\n")
        
        for i, entry in enumerate(self.entries, 1):
            lines.append(f"Entry #{i}")
            lines.append(str(entry))
            lines.append("")
        
        return "\n".join(lines)
