# logging_config.py
"""
Configuración centralizada del logging para toda la aplicación.
"""

import logging
from logging_driver import setup_logging, setup_default_logging, add_custom_handler


def configure_application_logging():
    """
    Configura el logging para toda la aplicación.
    Llama a esta función al inicio de tu aplicación.
    """
    
    # OPCIÓN 1: Configuración detallada
    setup_logging(
        level=logging.DEBUG,  # Cambia a logging.INFO en producción
        format='%(asctime)s - %(name)-20s - %(levelname)-8s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        filename='logs/iot_system.log',
        max_bytes=10 * 1024 * 1024,  # 10MB
        backup_count=5,
        encoding='utf-8',
        force=True  # Permite reconfigurar si ya estaba configurado
    )
    
    # OPCIÓN 2: Configuración simplificada
    # setup_default_logging(
    #     level='DEBUG',
    #     log_to_file=True,
    #     log_to_console=True,
    #     log_dir='logs'
    # )
    
    # Configurar logger raíz
    root_logger = logging.getLogger()
    root_logger.info("Logging configurado correctamente")
    
    # Opcional: Configurar niveles específicos por módulo
    # logging.getLogger('urllib3').setLevel(logging.WARNING)
    # logging.getLogger('websocket').setLevel(logging.WARNING)


def configure_production_logging():
    """Configuración para entorno de producción."""
    setup_logging(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        filename='logs/production.log',
        disable_console=False,  # Mantener consola para errores
        force=True
    )


def configure_development_logging():
    """Configuración para entorno de desarrollo."""
    # Handler colorizado para desarrollo
    try:
        from colorlog import ColoredFormatter
        import colorlog
        
        formatter = ColoredFormatter(
            '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S',
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )
        
        console_handler = colorlog.StreamHandler()
        console_handler.setFormatter(formatter)
        
        setup_logging(
            level=logging.DEBUG,
            handlers=[console_handler],
            force=True
        )
    except ImportError:
        # Fallback a logging estándar si colorlog no está instalado
        setup_default_logging(
            level='DEBUG',
            log_to_file=False,
            log_to_console=True
        )