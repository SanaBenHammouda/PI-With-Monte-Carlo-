"""
Module pour gérer les erreurs du système WMIC.
"""
from typing import Optional
from exceptions import WMICNotInstalledError


class ErrorHandler:
    """
    Gère les erreurs et détermine quand les lever selon la configuration.
    """
    
    def should_raise_error(
        self,
        parameter: Optional[str],
        wmic_installed: bool
    ) -> bool:
        """
        Détermine si une erreur doit être levée.
        
        Args:
            parameter: Valeur du paramètre ('Y', 'N', ou None)
            wmic_installed: True si WMIC est installé
            
        Returns:
            True si une erreur doit être levée, False sinon
        """
        # Erreur uniquement si paramètre='Y' ET WMIC non installé
        return parameter == 'Y' and not wmic_installed
    
    def handle_wmic_not_installed(self, parameter: str) -> WMICNotInstalledError:
        """
        Gère l'erreur WMIC non installé.
        
        Args:
            parameter: Valeur du paramètre
            
        Returns:
            WMICNotInstalledError à lever
        """
        return WMICNotInstalledError()
    
    def get_error_message(self, error_type: str, **kwargs) -> str:
        """
        Génère un message d'erreur approprié.
        
        Args:
            error_type: Type d'erreur
            **kwargs: Arguments additionnels pour le message
            
        Returns:
            Message d'erreur formaté
        """
        messages = {
            'wmic_not_installed': (
                "WMIC is not installed on this server. "
                "Please install WMIC or set the parameter to 'N'."
            ),
            'invalid_parameter': (
                f"Invalid parameter value '{kwargs.get('value')}'. "
                f"Allowed values are: 'Y', 'N', or undefined."
            ),
            'config_corrupted': (
                f"Configuration file '{kwargs.get('filepath')}' is corrupted. "
                f"Resetting to default configuration."
            ),
            'windows_version': (
                f"Windows version '{kwargs.get('version')}' may not be fully supported."
            )
        }
        
        return messages.get(error_type, "Unknown error occurred.")
    
    def get_actionable_message(
        self,
        parameter: Optional[str],
        wmic_installed: bool
    ) -> str:
        """
        Génère un message actionnable basé sur l'état du système.
        
        Args:
            parameter: Valeur du paramètre
            wmic_installed: Statut d'installation WMIC
            
        Returns:
            Message actionnable pour l'utilisateur
        """
        if parameter == 'Y' and not wmic_installed:
            return (
                "ERROR: WMIC is not installed but parameter is set to 'Y'.\n"
                "Actions:\n"
                "  1. Install WMIC on this server, OR\n"
                "  2. Set parameter to 'N': python src/main.py set-parameter --value N"
            )
        elif parameter == 'N' and not wmic_installed:
            return (
                "INFO: WMIC is not installed and parameter is set to 'N'.\n"
                "No action required. System will operate without WMIC."
            )
        elif parameter is None and not wmic_installed:
            return (
                "INFO: WMIC is not installed and parameter is undefined (default).\n"
                "No action required. System will operate without WMIC."
            )
        elif wmic_installed:
            return (
                "INFO: WMIC is installed and available.\n"
                f"Current parameter: {parameter if parameter else 'undefined (default: N)'}"
            )
        
        return "System status: OK"
