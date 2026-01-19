"""
Interface en ligne de commande pour le système WMIC.
"""
import argparse
import sys
from wmic_system import WMICSystem
from logger_setup import setup_logger, log_info, log_error
from exceptions import WMICNotInstalledError, InvalidParameterError, ConfigurationFileError


def cmd_check(args):
    """Commande: Vérifier le statut WMIC."""
    system = WMICSystem(args.config_file, args.journal_file)
    
    try:
        system.check_wmic()
        print("\n✓ WMIC check completed successfully")
        return 0
    except WMICNotInstalledError as e:
        print(f"\n✗ ERROR: {str(e)}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {str(e)}")
        log_error("Unexpected error during check", e)
        return 1


def cmd_set_parameter(args):
    """Commande: Définir le paramètre WMIC."""
    system = WMICSystem(args.config_file, args.journal_file)
    
    # Convertir 'default' en None
    value = args.value
    if value and value.lower() == 'default':
        value = None
    
    try:
        system.set_parameter(value)
        print(f"\n✓ Parameter set to: {value if value else 'undefined (default)'}")
        return 0
    except InvalidParameterError as e:
        print(f"\n✗ ERROR: {str(e)}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {str(e)}")
        log_error("Unexpected error setting parameter", e)
        return 1


def cmd_status(args):
    """Commande: Afficher le rapport de statut."""
    system = WMICSystem(args.config_file, args.journal_file)
    
    try:
        status = system.get_status()
        print(status.generate_report())
        return 0
    except Exception as e:
        print(f"\n✗ Error generating status report: {str(e)}")
        log_error("Error generating status", e)
        return 1


def cmd_journal(args):
    """Commande: Afficher le journal CR."""
    system = WMICSystem(args.config_file, args.journal_file)
    
    try:
        if args.last:
            # Afficher seulement la dernière entrée
            entry = system.get_last_cr_entry()
            if entry:
                print(entry)
            else:
                print("\nNo CR journal entries found.")
        else:
            # Afficher toutes les entrées
            entries = system.get_all_cr_entries()
            print(entries)
        return 0
    except Exception as e:
        print(f"\n✗ Error reading journal: {str(e)}")
        log_error("Error reading journal", e)
        return 1


def cmd_reset(args):
    """Commande: Réinitialiser la configuration."""
    system = WMICSystem(args.config_file, args.journal_file)
    
    try:
        system.reset_configuration()
        print("\n✓ Configuration reset to default (parameter: undefined)")
        return 0
    except Exception as e:
        print(f"\n✗ Error resetting configuration: {str(e)}")
        log_error("Error resetting configuration", e)
        return 1


def main():
    """Point d'entrée principal."""
    parser = argparse.ArgumentParser(
        description='WMIC Parameter Management System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check WMIC status
  python src/main.py check
  
  # Set parameter to Y (enable WMIC)
  python src/main.py set-parameter --value Y
  
  # Set parameter to N (disable WMIC)
  python src/main.py set-parameter --value N
  
  # Set parameter to default (undefined)
  python src/main.py set-parameter --value default
  
  # Show system status
  python src/main.py status
  
  # Show CR journal
  python src/main.py journal
  
  # Show last CR entry only
  python src/main.py journal --last
  
  # Reset configuration
  python src/main.py reset
        """
    )
    
    # Arguments globaux
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Set logging level (default: INFO)'
    )
    parser.add_argument(
        '--config-file',
        default='config/config.json',
        help='Path to configuration file (default: config/config.json)'
    )
    parser.add_argument(
        '--journal-file',
        default='journal/cr_journal.json',
        help='Path to CR journal file (default: journal/cr_journal.json)'
    )
    
    # Sous-commandes
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Commande: check
    parser_check = subparsers.add_parser(
        'check',
        help='Check WMIC installation status and handle errors based on configuration'
    )
    parser_check.set_defaults(func=cmd_check)
    
    # Commande: set-parameter
    parser_set = subparsers.add_parser(
        'set-parameter',
        help='Set the WMIC parameter value'
    )
    parser_set.add_argument(
        '--value',
        required=True,
        help="Parameter value: 'Y', 'N', or 'default' (undefined)"
    )
    parser_set.set_defaults(func=cmd_set_parameter)
    
    # Commande: status
    parser_status = subparsers.add_parser(
        'status',
        help='Display system status report'
    )
    parser_status.set_defaults(func=cmd_status)
    
    # Commande: journal
    parser_journal = subparsers.add_parser(
        'journal',
        help='Display CR journal entries'
    )
    parser_journal.add_argument(
        '--last',
        action='store_true',
        help='Show only the last entry'
    )
    parser_journal.set_defaults(func=cmd_journal)
    
    # Commande: reset
    parser_reset = subparsers.add_parser(
        'reset',
        help='Reset configuration to default values'
    )
    parser_reset.set_defaults(func=cmd_reset)
    
    # Parser les arguments
    args = parser.parse_args()
    
    # Configurer le logger
    setup_logger(log_level=args.log_level)
    
    # Vérifier qu'une commande a été fournie
    if not args.command:
        parser.print_help()
        return 1
    
    # Exécuter la commande
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
