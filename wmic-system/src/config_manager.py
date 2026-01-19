"""
Module pour gérer la configuration du système WMIC.
"""
import json
import os
from datetime import datetime
from typing import Optional
from exceptions import InvalidParameterError, ConfigurationFileError


class ConfigurationManager:
    """
    Gère les paramètres de configuration du système WMIC.
    """
    
    VALID_PARAMETERS = ['Y', 'N', None]
    DEFAULT_PARAMETER = None  # Équivalent à 'N'
    
    def __init__(self, config_file_path: str = 'config/config.json'):
        """
        Initialise le gestionnaire de configuration.
        
        Args:
            config_file_path: Chemin vers le fichier de configuration
        """
        self.config_file_path = config_file_path
        self.parameter_value: Optional[str] = None
        self.last_updated: Optional[str] = None
        self.version: str = "1.0"
        self.is_valid: bool = False
    
    def load_configuration(self) -> None:
        """
        Charge la configuration depuis le fichier JSON.
        
        Raises:
            ConfigurationFileError: Si le fichier est corrompu
        """
        try:
            if os.path.exists(self.config_file_path):
                with open(self.config_file_path, 'r') as f:
                    data = json.load(f)
                
                # Charger les valeurs
                param = data.get('wmic_parameter')
                # Convertir 'null' ou valeur vide en None
                if param == 'null' or param == '':
                    param = None
                
                self.parameter_value = param
                self.last_updated = data.get('last_updated')
                self.version = data.get('version', '1.0')
                
                # Valider la configuration chargée
                if not self.validate_parameter(self.parameter_value):
                    raise ConfigurationFileError(
                        self.config_file_path,
                        f"Invalid parameter value in config file: {self.parameter_value}"
                    )
                
                self.is_valid = True
            else:
                # Fichier n'existe pas, utiliser les valeurs par défaut
                self.parameter_value = self.DEFAULT_PARAMETER
                self.last_updated = datetime.now().isoformat()
                self.is_valid = True
                # Créer le fichier avec les valeurs par défaut
                self.save_configuration()
        
        except json.JSONDecodeError as e:
            raise ConfigurationFileError(
                self.config_file_path,
                f"JSON decode error: {str(e)}"
            )
        except Exception as e:
            if isinstance(e, ConfigurationFileError):
                raise
            raise ConfigurationFileError(
                self.config_file_path,
                f"Unexpected error loading configuration: {str(e)}"
            )
    
    def save_configuration(self) -> None:
        """
        Sauvegarde la configuration dans le fichier JSON.
        """
        # Créer le répertoire si nécessaire
        os.makedirs(os.path.dirname(self.config_file_path), exist_ok=True)
        
        # Mettre à jour le timestamp
        self.last_updated = datetime.now().isoformat()
        
        # Préparer les données
        data = {
            'wmic_parameter': self.parameter_value,
            'last_updated': self.last_updated,
            'version': self.version
        }
        
        # Sauvegarder
        with open(self.config_file_path, 'w') as f:
            json.dump(data, f, indent=4)
    
    def validate_parameter(self, value: Optional[str]) -> bool:
        """
        Valide une valeur de paramètre.
        
        Args:
            value: Valeur à valider ('Y', 'N', ou None)
            
        Returns:
            True si la valeur est valide, False sinon
        """
        return value in self.VALID_PARAMETERS
    
    def get_parameter(self) -> Optional[str]:
        """
        Retourne la valeur actuelle du paramètre.
        
        Returns:
            Valeur du paramètre ('Y', 'N', ou None)
        """
        return self.parameter_value
    
    def set_parameter(self, value: Optional[str]) -> None:
        """
        Définit la valeur du paramètre.
        
        Args:
            value: Nouvelle valeur ('Y', 'N', ou None)
            
        Raises:
            InvalidParameterError: Si la valeur est invalide
        """
        if not self.validate_parameter(value):
            raise InvalidParameterError(value)
        
        self.parameter_value = value
        self.is_valid = True
        self.save_configuration()
    
    def reset_to_default(self) -> None:
        """
        Réinitialise la configuration aux valeurs par défaut.
        """
        self.parameter_value = self.DEFAULT_PARAMETER
        self.last_updated = datetime.now().isoformat()
        self.version = "1.0"
        self.is_valid = True
        self.save_configuration()
    
    def get_effective_parameter(self) -> str:
        """
        Retourne le paramètre effectif (convertit None en 'N').
        
        Returns:
            'Y' ou 'N'
        """
        if self.parameter_value is None:
            return 'N'
        return self.parameter_value
    
    def __str__(self) -> str:
        """Représentation textuelle de la configuration."""
        param_display = self.parameter_value if self.parameter_value is not None else 'undefined'
        return (f"Configuration(parameter={param_display}, "
                f"last_updated={self.last_updated}, "
                f"valid={self.is_valid})")
