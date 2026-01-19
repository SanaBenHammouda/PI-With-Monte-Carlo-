"""
Exceptions personnalisées pour le système WMIC.
"""


class WMICSystemError(Exception):
    """Classe de base pour toutes les erreurs du système WMIC."""
    pass


class WMICNotInstalledError(WMICSystemError):
    """
    Levée quand WMIC n'est pas installé et que le paramètre est défini à 'Y'.
    """
    def __init__(self, message=None):
        if message is None:
            message = (
                "WMIC is not installed on this server. "
                "Please install WMIC or set the parameter to 'N'."
            )
        super().__init__(message)


class InvalidParameterError(WMICSystemError):
    """
    Levée quand une valeur de paramètre invalide est fournie.
    """
    def __init__(self, value, message=None):
        if message is None:
            message = (
                f"Invalid parameter value '{value}'. "
                f"Allowed values are: 'Y', 'N', or undefined (None)."
            )
        self.value = value
        super().__init__(message)


class ConfigurationFileError(WMICSystemError):
    """
    Levée quand le fichier de configuration est corrompu ou inaccessible.
    """
    def __init__(self, filepath, message=None):
        if message is None:
            message = (
                f"Configuration file '{filepath}' is corrupted or inaccessible. "
                f"The system will reset to default configuration."
            )
        self.filepath = filepath
        super().__init__(message)


class WindowsVersionError(WMICSystemError):
    """
    Levée quand la version de Windows n'est pas supportée.
    """
    def __init__(self, version, message=None):
        if message is None:
            message = (
                f"Windows version '{version}' is not supported. "
                f"Minimum required: Windows Server 2012 R2 or Windows 8.1."
            )
        self.version = version
        super().__init__(message)
