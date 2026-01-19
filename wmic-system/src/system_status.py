"""
Module pour générer des rapports de statut système.
"""
from typing import Optional
from datetime import datetime


class SystemStatus:
    """
    Génère des rapports de statut pour le système WMIC.
    """
    
    def __init__(
        self,
        wmic_installed: bool,
        parameter_value: Optional[str],
        windows_version: str,
        wmic_deprecated: bool,
        last_error: Optional[str] = None,
        wmic_path: Optional[str] = None
    ):
        """
        Initialise le statut système.
        
        Args:
            wmic_installed: True si WMIC est installé
            parameter_value: Valeur du paramètre de configuration
            windows_version: Version de Windows
            wmic_deprecated: True si WMIC est déprécié
            last_error: Dernière erreur rencontrée
            wmic_path: Chemin vers WMIC
        """
        self.wmic_installed = wmic_installed
        self.parameter_value = parameter_value
        self.windows_version = windows_version
        self.wmic_deprecated = wmic_deprecated
        self.last_error = last_error
        self.wmic_path = wmic_path
        self.timestamp = datetime.now()
    
    def is_healthy(self) -> bool:
        """
        Détermine si le système est en bon état.
        
        Returns:
            True si le système est sain, False sinon
        """
        # Le système est sain si:
        # 1. Pas d'erreur récente, OU
        # 2. Paramètre != 'Y' (donc pas d'erreur attendue)
        if self.last_error is None:
            return True
        
        if self.parameter_value != 'Y':
            return True
        
        # Si paramètre='Y' et il y a une erreur, système malsain
        return False
    
    def generate_report(self) -> str:
        """
        Génère un rapport de statut formaté.
        
        Returns:
            Rapport de statut sous forme de chaîne
        """
        lines = [
            "",
            "=" * 70,
            "WMIC SYSTEM STATUS REPORT",
            "=" * 70,
            f"Timestamp:           {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Windows Version:     {self.windows_version}",
            "",
            "--- WMIC Status ---",
            f"WMIC Installed:      {'Yes' if self.wmic_installed else 'No'}",
        ]
        
        if self.wmic_path:
            lines.append(f"WMIC Path:           {self.wmic_path}")
        
        lines.append(f"WMIC Deprecated:     {'Yes' if self.wmic_deprecated else 'No'}")
        
        if self.wmic_deprecated:
            lines.append("  ⚠ Warning: WMIC is deprecated. Consider using PowerShell or WMI alternatives.")
        
        lines.extend([
            "",
            "--- Configuration ---",
            f"Parameter Value:     {self.parameter_value if self.parameter_value else 'undefined (default)'}",
            f"Effective Behavior:  {'WMIC Enabled' if self.parameter_value == 'Y' else 'WMIC Disabled'}",
            "",
            "--- System Health ---",
        ])
        
        if self.last_error:
            lines.append(f"Last Error:          {self.last_error}")
        else:
            lines.append(f"Last Error:          None")
        
        health_status = "OK" if self.is_healthy() else "ERROR"
        health_symbol = "✓" if self.is_healthy() else "✗"
        lines.append(f"System Health:       {health_symbol} {health_status}")
        
        # Ajouter des recommandations
        lines.extend([
            "",
            "--- Recommendations ---"
        ])
        
        if self.parameter_value == 'Y' and not self.wmic_installed:
            lines.extend([
                "  ⚠ Parameter is set to 'Y' but WMIC is not installed.",
                "  → Install WMIC or set parameter to 'N'",
                "  → Command: python src/main.py set-parameter --value N"
            ])
        elif not self.wmic_installed:
            lines.extend([
                "  ℹ WMIC is not installed, but system is configured correctly.",
                "  → No action required."
            ])
        elif self.wmic_deprecated:
            lines.extend([
                "  ℹ WMIC is deprecated on this Windows version.",
                "  → Consider migrating to PowerShell or Python WMI alternatives."
            ])
        else:
            lines.append("  ✓ System is properly configured.")
        
        lines.append("=" * 70)
        lines.append("")
        
        return "\n".join(lines)
    
    def get_summary(self) -> str:
        """
        Génère un résumé court du statut.
        
        Returns:
            Résumé du statut
        """
        health = "OK" if self.is_healthy() else "ERROR"
        wmic_status = "Installed" if self.wmic_installed else "Not Installed"
        param = self.parameter_value if self.parameter_value else "undefined"
        
        return f"Status: {health} | WMIC: {wmic_status} | Parameter: {param}"
    
    def __str__(self) -> str:
        """Représentation textuelle du statut."""
        return self.generate_report()
