"""
Module pour configurer le système de logging.
"""
import logging
import os
from datetime import datetime


def setup_logger(
    log_level: str = 'INFO',
    log_file: str = 'logs/wmic_system.log',
    logger_name: str = 'wmic_system'
) -> logging.Logger:
    """
    Configure et retourne un logger pour le système WMIC.
    
    Args:
        log_level: Niveau de log ('DEBUG', 'INFO', 'WARNING', 'ERROR')
        log_file: Chemin vers le fichier de log
        logger_name: Nom du logger
        
    Returns:
        Logger configuré
    """
    # Créer le répertoire de logs si nécessaire
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Créer le logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Éviter les doublons de handlers
    if logger.handlers:
        return logger
    
    # Format des logs
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter(log_format, date_format)
    
    # Handler pour fichier
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(getattr(logging, log_level.upper()))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Handler pour console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger


# Instance globale du logger
_logger = None


def get_logger() -> logging.Logger:
    """
    Retourne l'instance globale du logger.
    
    Returns:
        Logger configuré
    """
    global _logger
    if _logger is None:
        _logger = setup_logger()
    return _logger


def log_info(message: str) -> None:
    """Log un message d'information."""
    get_logger().info(message)


def log_warning(message: str) -> None:
    """Log un avertissement."""
    get_logger().warning(message)


def log_error(message: str, exception: Exception = None) -> None:
    """
    Log une erreur.
    
    Args:
        message: Message d'erreur
        exception: Exception optionnelle
    """
    if exception:
        get_logger().error(f"{message}: {str(exception)}", exc_info=True)
    else:
        get_logger().error(message)


def log_debug(message: str) -> None:
    """Log un message de débogage."""
    get_logger().debug(message)
