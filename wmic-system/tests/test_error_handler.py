"""
Tests pour ErrorHandler.
"""
import pytest
from hypothesis import given, strategies as st, settings
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from error_handler import ErrorHandler
from exceptions import WMICNotInstalledError


# ============================================================================
# TESTS DE PROPRIÉTÉS
# ============================================================================

@given(
    parameter=st.sampled_from(['Y', 'N', None]),
    wmic_installed=st.booleans()
)
@settings(max_examples=100)
def test_property_3_conditional_error_generation(parameter, wmic_installed):
    """
    Feature: wmic-parameter-handler, Property 3: Génération d'erreur conditionnelle
    
    Pour tout état du système, une erreur "not installed" doit être générée
    si et seulement si le paramètre est 'Y' ET WMIC n'est pas installé.
    
    Valide: Exigences 3.1, 3.2, 3.3
    """
    handler = ErrorHandler()
    should_error = handler.should_raise_error(parameter, wmic_installed)
    
    # Vérifier la logique conditionnelle
    expected_error = (parameter == 'Y' and not wmic_installed)
    assert should_error == expected_error, \
        f"Error generation mismatch: parameter={parameter}, wmic_installed={wmic_installed}"


@given(wmic_installed=st.booleans())
@settings(max_examples=100)
def test_property_4_safe_default_behavior(wmic_installed):
    """
    Feature: wmic-parameter-handler, Property 4: Comportement par défaut sûr
    
    Pour tout système où le paramètre est undefined (None),
    le comportement doit être identique au paramètre 'N' (pas d'erreur).
    
    Valide: Exigences 5.1, 5.2, 5.3
    """
    handler = ErrorHandler()
    
    # Tester avec None (undefined)
    should_error_none = handler.should_raise_error(None, wmic_installed)
    
    # Tester avec 'N'
    should_error_n = handler.should_raise_error('N', wmic_installed)
    
    # Les deux doivent être identiques (pas d'erreur)
    assert should_error_none == should_error_n == False, \
        "Default (None) behavior should match 'N' behavior (no error)"


# ============================================================================
# TESTS UNITAIRES
# ============================================================================

def test_should_raise_error_parameter_y_wmic_absent():
    """Teste qu'une erreur est levée quand paramètre='Y' et WMIC absent."""
    handler = ErrorHandler()
    assert handler.should_raise_error('Y', False) is True


def test_should_not_raise_error_parameter_n_wmic_absent():
    """Teste qu'aucune erreur n'est levée quand paramètre='N' et WMIC absent."""
    handler = ErrorHandler()
    assert handler.should_raise_error('N', False) is False


def test_should_not_raise_error_parameter_none_wmic_absent():
    """Teste qu'aucune erreur n'est levée quand paramètre=None et WMIC absent."""
    handler = ErrorHandler()
    assert handler.should_raise_error(None, False) is False


def test_should_not_raise_error_parameter_y_wmic_present():
    """Teste qu'aucune erreur n'est levée quand paramètre='Y' et WMIC présent."""
    handler = ErrorHandler()
    assert handler.should_raise_error('Y', True) is False


def test_handle_wmic_not_installed():
    """Teste la génération de l'exception WMICNotInstalledError."""
    handler = ErrorHandler()
    error = handler.handle_wmic_not_installed('Y')
    assert isinstance(error, WMICNotInstalledError)
    assert "not installed" in str(error).lower()


def test_get_error_message_wmic_not_installed():
    """Teste la génération du message d'erreur WMIC non installé."""
    handler = ErrorHandler()
    message = handler.get_error_message('wmic_not_installed')
    assert "not installed" in message.lower()
    assert "wmic" in message.lower()


def test_get_error_message_invalid_parameter():
    """Teste la génération du message d'erreur paramètre invalide."""
    handler = ErrorHandler()
    message = handler.get_error_message('invalid_parameter', value='X')
    assert "invalid" in message.lower()
    assert "'X'" in message


def test_get_actionable_message_parameter_y_wmic_absent():
    """Teste le message actionnable pour paramètre='Y' et WMIC absent."""
    handler = ErrorHandler()
    message = handler.get_actionable_message('Y', False)
    assert "ERROR" in message
    assert "not installed" in message.lower()
    assert "Actions" in message or "action" in message.lower()


def test_get_actionable_message_parameter_n_wmic_absent():
    """Teste le message actionnable pour paramètre='N' et WMIC absent."""
    handler = ErrorHandler()
    message = handler.get_actionable_message('N', False)
    assert "INFO" in message
    assert "No action required" in message or "no action" in message.lower()


def test_get_actionable_message_parameter_none_wmic_absent():
    """Teste le message actionnable pour paramètre=None et WMIC absent."""
    handler = ErrorHandler()
    message = handler.get_actionable_message(None, False)
    assert "INFO" in message
    assert "undefined" in message.lower() or "default" in message.lower()


def test_get_actionable_message_wmic_present():
    """Teste le message actionnable quand WMIC est présent."""
    handler = ErrorHandler()
    message = handler.get_actionable_message('Y', True)
    assert "INFO" in message
    assert "installed" in message.lower() or "available" in message.lower()
