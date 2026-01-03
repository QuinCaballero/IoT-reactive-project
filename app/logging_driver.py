"""
Logging Driver con Configuración Centralizada
Permite configurar logging.basicConfig desde un único punto.
"""

import logging
import logging.handlers
from pathlib import Path
import sys
from typing import Optional, Dict, Any
import json
import os


class CentralizedLogging:
    """
    Clase para configuración centralizada del logging.
    Usa patrón Singleton para asegurar una única configuración.
    """
    
    _instance = None
    _configured = False
    
    def __new__(cls):
        """Patrón Singleton."""
        if cls._instance is None:
            cls._instance = super(CentralizedLogging, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.default_config = {
                'level': logging.INFO,
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S',
                'filename': None,
                'filemode': 'a',
                'stream': None,
                'handlers': None,
                'force': False,
                'encoding': 'utf-8',
                'errors': None
            }
            self.custom_handlers = []
            self.initialized = True
    
    def configure(self, **kwargs):
        """
        Configura el logging centralizado.
        
        Args:
            **kwargs: Parámetros para logging.basicConfig
                     (level, format, filename, etc.)
        
        Ejemplo:
            configure(level=logging.DEBUG, 
                     filename='app.log',
                     format='%(asctime)s - %(message)s')
        """
        if self._configured and not kwargs.get('force', False):
            print("Logging ya configurado. Usa force=True para reconfigurar.")
            return
        
        # Combinar configuración por defecto con personalizada
        config = self.default_config.copy()
        config.update(kwargs)
        
        # Configurar handlers personalizados si se especifican
        if 'handlers' in kwargs:
            config['handlers'] = kwargs['handlers']
        elif config.get('filename') or self.custom_handlers:
            config['handlers'] = self._create_handlers(config)
        
        # Aplicar configuración
        logging.basicConfig(**config)
        self._configured = True
        
        # Log de configuración aplicada
        root_logger = logging.getLogger()
        root_logger.debug(f"Logging configurado: {config}")
    
    def _create_handlers(self, config: Dict[str, Any]) -> list:
        """Crea handlers basados en la configuración."""
        handlers = []
        
        # Handler para consola (siempre activo a menos que se desactive explícitamente)
        if not config.get('disable_console', False):
            console_handler = logging.StreamHandler(sys.stdout)
            console_formatter = logging.Formatter(
                config.get('format', self.default_config['format']),
                datefmt=config.get('datefmt', self.default_config['datefmt'])
            )
            console_handler.setFormatter(console_formatter)
            console_handler.setLevel(config['level'])
            handlers.append(console_handler)
        
        # Handler para archivo si se especifica filename
        if config.get('filename'):
            # Crear directorio si no existe
            log_dir = os.path.dirname(config['filename']) or '.'
            if log_dir:
                Path(log_dir).mkdir(exist_ok=True)
            
            file_handler = logging.handlers.RotatingFileHandler(
                config['filename'],
                maxBytes=config.get('max_bytes', 10 * 1024 * 1024),  # 10MB por defecto
                backupCount=config.get('backup_count', 5),
                encoding=config.get('encoding', 'utf-8')
            )
            file_formatter = logging.Formatter(
                config.get('format', self.default_config['format']),
                datefmt=config.get('datefmt', self.default_config['datefmt'])
            )
            file_handler.setFormatter(file_formatter)
            file_handler.setLevel(config['level'])
            handlers.append(file_handler)
        
        # Agregar handlers personalizados
        handlers.extend(self.custom_handlers)
        
        return handlers
    
    def add_custom_handler(self, handler: logging.Handler):
        """Añade un handler personalizado."""
        self.custom_handlers.append(handler)
    
    def setup_default_config(self, 
                           level: str = 'INFO',
                           log_to_file: bool = True,
                           log_to_console: bool = True,
                           log_dir: str = 'logs'):
        """
        Configuración por defecto simplificada.
        
        Args:
            level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_to_file: Habilitar logging a archivo
            log_to_console: Habilitar logging a consola
            log_dir: Directorio para archivos de log
        """
        # Convertir nivel de string a constante de logging
        level_value = getattr(logging, level.upper(), logging.INFO)
        
        config = {
            'level': level_value,
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'force': True
        }
        
        if log_to_file:
            # Crear directorio de logs
            Path(log_dir).mkdir(exist_ok=True)
            config['filename'] = str(Path(log_dir) / 'application.log')
            config['max_bytes'] = 10 * 1024 * 1024  # 10MB
            config['backup_count'] = 5
        
        if not log_to_console:
            config['disable_console'] = True
        
        self.configure(**config)
    
    def get_config(self) -> Dict[str, Any]:
        """Obtiene la configuración actual."""
        root_logger = logging.getLogger()
        config = {
            'level': root_logger.level,
            'handlers_count': len(root_logger.handlers),
            'configured': self._configured
        }
        return config
    
    def reset(self):
        """Reinicia la configuración del logging."""
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        self._configured = False
        self.custom_handlers = []


# Instancia global
_logging_manager = CentralizedLogging()


# Funciones de conveniencia para configuración
def setup_logging(**kwargs):
    """
    Configura el logging con los parámetros especificados.
    
    Ejemplos:
        setup_logging(level='DEBUG', filename='app.log')
        setup_logging(level=logging.INFO, format='%(message)s')
    """
    _logging_manager.configure(**kwargs)


def setup_default_logging(level: str = 'INFO',
                         log_to_file: bool = True,
                         log_to_console: bool = True,
                         log_dir: str = 'logs'):
    """
    Configuración por defecto simplificada.
    """
    _logging_manager.setup_default_config(
        level=level,
        log_to_file=log_to_file,
        log_to_console=log_to_console,
        log_dir=log_dir
    )


def add_custom_handler(handler: logging.Handler):
    """Añade un handler personalizado."""
    _logging_manager.add_custom_handler(handler)


def get_logging_config() -> Dict[str, Any]:
    """Obtiene la configuración actual del logging."""
    return _logging_manager.get_config()


# Funciones de logging para uso directo (igual que antes)
def get_logger(name: str) -> logging.Logger:
    """Obtiene un logger con el nombre especificado."""
    return logging.getLogger(name)


def debug(msg: str, *args, **kwargs):
    """Log a message with severity 'DEBUG'."""
    return logging.debug(msg, *args, **kwargs)


def info(msg: str, *args, **kwargs):
    """Log a message with severity 'INFO'."""
    return logging.info(msg, *args, **kwargs)


def warning(msg: str, *args, **kwargs):
    """Log a message with severity 'WARNING'."""
    return logging.warning(msg, *args, **kwargs)


def error(msg: str, *args, **kwargs):
    """Log a message with severity 'ERROR'."""
    return logging.error(msg, *args, **kwargs)


def critical(msg: str, *args, **kwargs):
    """Log a message with severity 'CRITICAL'."""
    return logging.critical(msg, *args, **kwargs)


def exception(msg: str, *args, **kwargs):
    """Log a message with severity 'ERROR' con información de excepción."""
    return logging.exception(msg, *args, **kwargs)


# Configuración automática por defecto (opcional)
# Puedes descomentar si quieres configuración automática:
# setup_default_logging()