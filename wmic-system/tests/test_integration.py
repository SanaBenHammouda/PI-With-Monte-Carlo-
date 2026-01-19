"""
Tests d'intégration pour le système WMIC complet.
"""
import pytest
import os
import sys
import tempfile
import shutil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from wmic_system import WMICSystem
from exceptions import WMICNotInstalledError, InvalidParameterError


class TestIntegration:
    """Tests d'intégration du système complet."""
    
    def setup_method(self):
        """Prépare un environnement de test temporaire."""
        self.test_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.test_dir, 'config.json')
        self.journal_file = os.path.join(self.test_dir, 'journal.json')
    
    def teardown_method(self):
        """Nettoie l'environnement de test."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_initialization(self):
        """Teste l'initialisation du système."""
        system = WMICSystem(self.config_file, self.journal_file)
        system.initialize()
        
        # Vérifier que la configuration est créée
        assert os.path.exists(self.config_file)
    
    def test_set_parameter_valid_values(self):
        """Teste la définition de paramètres valides."""
        system = WMICSystem(self.config_file, self.journal_file)
        system.initialize()
        
        # Tester 'Y'
        system.set_parameter('Y')
        assert system.config_manager.get_parameter() == 'Y'
        
        # Tester 'N'
        system.set_parameter('N')
        assert system.config_manager.get_parameter() == 'N'
        
        # Tester None
        system.set_parameter(None)
        assert system.config_manager.get_parameter() is None
    
    def test_set_parameter_invalid_value(self):
        """Teste le rejet de paramètres invalides."""
        system = WMICSystem(self.config_file, self.journal_file)
        system.initialize()
        
        with pytest.raises(InvalidParameterError):
            system.set_parameter('X')
    
    def test_check_wmic_parameter_n(self):
        """Teste la vérification WMIC avec paramètre='N'."""
        system = WMICSystem(self.config_file, self.journal_file)
        system.initialize()
        system.set_parameter('N')
        
        # Ne devrait pas lever d'erreur, peu importe si WMIC est installé
        try:
            result = system.check_wmic()
            assert result is True
        except WMICNotInstalledError:
            pytest.fail("Should not raise error with parameter='N'")
    
    def test_check_wmic_parameter_none(self):
        """Teste la vérification WMIC avec paramètre=None (default)."""
        system = WMICSystem(self.config_file, self.journal_file)
        system.initialize()
        system.set_parameter(None)
        
        # Ne devrait pas lever d'erreur (comportement par défaut)
        try:
            result = system.check_wmic()
            assert result is True
        except WMICNotInstalledError:
            pytest.fail("Should not raise error with parameter=None")
    
    def test_status_report_generation(self):
        """Teste la génération du rapport de statut."""
        system = WMICSystem(self.config_file, self.journal_file)
        system.initialize()
        
        status = system.get_status()
        assert status is not None
        
        report = status.generate_report()
        assert "WMIC SYSTEM STATUS REPORT" in report
        assert "Windows Version" in report
        assert "WMIC Installed" in report
    
    def test_cr_journal_creation(self):
        """Teste la création d'entrées dans le journal CR."""
        system = WMICSystem(self.config_file, self.journal_file)
        system.initialize()
        system.set_parameter('N')
        
        # Effectuer une vérification (crée une entrée CR)
        system.check_wmic()
        
        # Vérifier que le journal existe
        assert os.path.exists(self.journal_file)
        
        # Vérifier qu'il y a au moins une entrée
        last_entry = system.get_last_cr_entry()
        assert last_entry is not None
        assert "CR Entry" in last_entry
    
    def test_configuration_persistence(self):
        """Teste la persistance de la configuration."""
        # Créer et configurer le système
        system1 = WMICSystem(self.config_file, self.journal_file)
        system1.initialize()
        system1.set_parameter('Y')
        
        # Créer une nouvelle instance et vérifier la persistance
        system2 = WMICSystem(self.config_file, self.journal_file)
        system2.initialize()
        
        assert system2.config_manager.get_parameter() == 'Y'
    
    def test_reset_configuration(self):
        """Teste la réinitialisation de la configuration."""
        system = WMICSystem(self.config_file, self.journal_file)
        system.initialize()
        
        # Définir un paramètre
        system.set_parameter('Y')
        assert system.config_manager.get_parameter() == 'Y'
        
        # Réinitialiser
        system.reset_configuration()
        assert system.config_manager.get_parameter() is None
    
    def test_multiple_cr_entries(self):
        """Teste la création de plusieurs entrées CR."""
        system = WMICSystem(self.config_file, self.journal_file)
        system.initialize()
        
        # Effectuer plusieurs opérations
        system.set_parameter('N')
        system.check_wmic()
        
        system.set_parameter('Y')
        try:
            system.check_wmic()
        except WMICNotInstalledError:
            pass  # Attendu si WMIC n'est pas installé
        
        # Vérifier qu'il y a plusieurs entrées
        all_entries = system.get_all_cr_entries()
        assert "Entry #" in all_entries
    
    def test_system_health_check(self):
        """Teste la vérification de santé du système."""
        system = WMICSystem(self.config_file, self.journal_file)
        system.initialize()
        system.set_parameter('N')
        
        status = system.get_status()
        
        # Avec paramètre='N', le système devrait être sain
        assert status.is_healthy() is True
