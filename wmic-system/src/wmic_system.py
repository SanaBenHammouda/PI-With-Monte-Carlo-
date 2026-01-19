"""
Classe principale du système de gestion WMIC.
"""
from typing import Optional
from wmic_detector import WMICDetector
from config_manager import ConfigurationManager
from error_handler import ErrorHandler
from cr_journal import CRJournalWriter
from system_status import SystemStatus
from logger_setup import log_info, log_warning, log_error, log_debug
from exceptions import WMICNotInstalledError, InvalidParameterError, ConfigurationFileError


class WMICSystem:
    """
    Système principal de gestion des paramètres WMIC.
    
    Intègre tous les composants pour fournir une interface unifiée.
    """
    
    def __init__(
        self,
        config_file: str = 'config/config.json',
        journal_file: str = 'journal/cr_journal.json'
    ):
        """
        Initialise le système WMIC.
        
        Args:
            config_file: Chemin vers le fichier de configuration
            journal_file: Chemin vers le fichier journal CR
        """
        self.detector = WMICDetector()
        self.config_manager = ConfigurationManager(config_file)
        self.error_handler = ErrorHandler()
        self.journal_writer = CRJournalWriter(journal_file)
        
        self._initialized = False
        self._last_error: Optional[str] = None
    
    def initialize(self) -> None:
        """
        Initialise le système en chargeant la configuration.
        
        Raises:
            ConfigurationFileError: Si la configuration est corrompue
        """
        try:
            log_info("Initializing WMIC system...")
            self.config_manager.load_configuration()
            self._initialized = True
            log_info("WMIC system initialized successfully")
        except ConfigurationFileError as e:
            log_error("Configuration file error", e)
            # Réinitialiser à la configuration par défaut
            self.config_manager.reset_to_default()
            self._initialized = True
            log_info("Configuration reset to default")
    
    def check_wmic(self) -> bool:
        """
        Vérifie le statut WMIC et gère les erreurs selon la configuration.
        
        Returns:
            True si la vérification réussit, False si une erreur est levée
            
        Raises:
            WMICNotInstalledError: Si paramètre='Y' et WMIC non installé
        """
        if not self._initialized:
            self.initialize()
        
        log_info("Checking WMIC status...")
        
        # Détecter WMIC
        wmic_installed = self.detector.is_wmic_installed()
        parameter = self.config_manager.get_parameter()
        
        log_debug(f"WMIC installed: {wmic_installed}")
        log_debug(f"Parameter value: {parameter}")
        
        # Vérifier si WMIC est déprécié
        if self.detector.is_wmic_deprecated():
            log_warning("WMIC is deprecated on this Windows version")
        
        # Déterminer si une erreur doit être levée
        should_error = self.error_handler.should_raise_error(parameter, wmic_installed)
        
        if should_error:
            error_msg = "WMIC is not installed"
            self._last_error = error_msg
            log_error(error_msg)
            
            # Documenter dans le journal CR
            self.journal_writer.write_wmic_status(parameter, wmic_installed, error=error_msg)
            
            # Lever l'erreur
            raise WMICNotInstalledError()
        else:
            # Pas d'erreur
            self._last_error = None
            
            # Message approprié
            actionable_msg = self.error_handler.get_actionable_message(parameter, wmic_installed)
            log_info(actionable_msg)
            
            # Documenter dans le journal CR
            self.journal_writer.write_wmic_status(parameter, wmic_installed, error=None)
            
            return True
    
    def set_parameter(self, value: Optional[str]) -> None:
        """
        Définit la valeur du paramètre WMIC.
        
        Args:
            value: Nouvelle valeur ('Y', 'N', ou None)
            
        Raises:
            InvalidParameterError: Si la valeur est invalide
        """
        if not self._initialized:
            self.initialize()
        
        log_info(f"Setting WMIC parameter to: {value}")
        
        try:
            self.config_manager.set_parameter(value)
            log_info(f"Parameter set successfully to: {value}")
        except InvalidParameterError as e:
            log_error("Invalid parameter value", e)
            raise
    
    def get_status(self) -> SystemStatus:
        """
        Génère un rapport de statut système.
        
        Returns:
            Objet SystemStatus contenant toutes les informations
        """
        if not self._initialized:
            self.initialize()
        
        # Collecter toutes les informations
        detection_report = self.detector.get_detection_report()
        parameter = self.config_manager.get_parameter()
        
        status = SystemStatus(
            wmic_installed=detection_report['wmic_installed'],
            parameter_value=parameter,
            windows_version=detection_report['windows_version'],
            wmic_deprecated=detection_report['wmic_deprecated'],
            last_error=self._last_error,
            wmic_path=detection_report['wmic_path']
        )
        
        return status
    
    def reset_configuration(self) -> None:
        """
        Réinitialise la configuration aux valeurs par défaut.
        """
        if not self._initialized:
            self.initialize()
        
        log_info("Resetting configuration to default...")
        self.config_manager.reset_to_default()
        self._last_error = None
        log_info("Configuration reset successfully")
    
    def get_last_cr_entry(self) -> Optional[str]:
        """
        Retourne la dernière entrée du journal CR.
        
        Returns:
            Dernière entrée formatée ou None
        """
        entry = self.journal_writer.get_last_entry()
        if entry:
            return self.journal_writer.format_entry(entry)
        return None
    
    def get_all_cr_entries(self) -> str:
        """
        Retourne toutes les entrées du journal CR.
        
        Returns:
            Toutes les entrées formatées
        """
        return self.journal_writer.format_all_entries()
