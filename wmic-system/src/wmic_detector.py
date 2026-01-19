"""
Module pour détecter l'installation et la disponibilité de WMIC.
"""
import os
import platform
import subprocess
from typing import Optional


class WMICDetector:
    """
    Détecte la présence et la disponibilité de WMIC sur le système Windows.
    """
    
    def __init__(self):
        """Initialise le détecteur WMIC."""
        self._wmic_path = None
        self._windows_version = None
        self._is_deprecated = None
    
    def is_wmic_installed(self) -> bool:
        """
        Vérifie si WMIC est installé sur le système.
        
        Returns:
            True si WMIC est installé et fonctionnel, False sinon
        """
        # Méthode 1: Vérifier l'existence du fichier wmic.exe
        wmic_path = self.get_wmic_path()
        if wmic_path and os.path.exists(wmic_path):
            # Méthode 2: Tenter d'exécuter WMIC pour confirmer
            try:
                result = subprocess.run(
                    [wmic_path, '/?'],
                    capture_output=True,
                    timeout=5,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                )
                return result.returncode == 0
            except (subprocess.TimeoutExpired, FileNotFoundError, PermissionError):
                return False
        
        return False
    
    def get_wmic_path(self) -> Optional[str]:
        """
        Retourne le chemin vers l'exécutable WMIC.
        
        Returns:
            Chemin vers wmic.exe ou None si non trouvé
        """
        if self._wmic_path is not None:
            return self._wmic_path
        
        # Vérifier dans System32
        if 'SystemRoot' in os.environ:
            system_root = os.environ['SystemRoot']
            wmic_path = os.path.join(system_root, 'System32', 'wmic.exe')
            if os.path.exists(wmic_path):
                self._wmic_path = wmic_path
                return wmic_path
        
        # Vérifier dans le PATH
        try:
            result = subprocess.run(
                ['where', 'wmic'],
                capture_output=True,
                timeout=5,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            if result.returncode == 0:
                wmic_path = result.stdout.decode().strip().split('\n')[0]
                self._wmic_path = wmic_path
                return wmic_path
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        return None
    
    def get_windows_version(self) -> str:
        """
        Retourne la version de Windows.
        
        Returns:
            Version de Windows (ex: "Windows 10", "Windows Server 2019")
        """
        if self._windows_version is not None:
            return self._windows_version
        
        try:
            # Obtenir les informations de version
            version_info = platform.platform()
            release = platform.release()
            
            # Construire une chaîne de version lisible
            if 'Windows' in version_info:
                self._windows_version = f"Windows {release}"
            else:
                self._windows_version = version_info
            
            return self._windows_version
        except Exception:
            return "Unknown Windows Version"
    
    def is_wmic_deprecated(self) -> bool:
        """
        Vérifie si WMIC est déprécié sur cette version de Windows.
        
        WMIC est déprécié depuis Windows 10 version 21H1 (build 19043).
        
        Returns:
            True si WMIC est déprécié, False sinon
        """
        if self._is_deprecated is not None:
            return self._is_deprecated
        
        try:
            # Obtenir le numéro de build Windows
            version = platform.version()
            # Format: "10.0.19043" pour Windows 10 21H1
            parts = version.split('.')
            
            if len(parts) >= 3:
                major = int(parts[0])
                minor = int(parts[1])
                build = int(parts[2])
                
                # Windows 10/11 (major=10) avec build >= 19043
                if major == 10 and build >= 19043:
                    self._is_deprecated = True
                    return True
        except (ValueError, IndexError):
            pass
        
        self._is_deprecated = False
        return False
    
    def get_detection_report(self) -> dict:
        """
        Génère un rapport complet de détection WMIC.
        
        Returns:
            Dictionnaire contenant toutes les informations de détection
        """
        return {
            'wmic_installed': self.is_wmic_installed(),
            'wmic_path': self.get_wmic_path(),
            'windows_version': self.get_windows_version(),
            'wmic_deprecated': self.is_wmic_deprecated()
        }
