import os
import sys
import logging

def configure_logging(is_production=None):
    """
    Configure application logging based on environment
    
    Args:
        is_production (bool, optional): Whether the app is running in production mode.
                                        If None, auto-detects based on frozen state.
    """

    if is_production is None:
        is_production = getattr(sys, 'frozen', False)
    
    logger = logging.getLogger() 
    
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')    
    
    if is_production:
        logger.setLevel(logging.ERROR)  

        try:
            if is_production:
                base_dir = os.path.dirname(sys.executable)
            else:
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            log_dir = os.path.join(base_dir, 'logs')
            os.makedirs(log_dir, exist_ok=True)
            
            # Add file handler for errors only
            error_log_path = os.path.join(log_dir, 'error.log')
            file_handler = logging.FileHandler(error_log_path)
            file_handler.setLevel(logging.ERROR)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception:
            pass
    else:
        logger.setLevel(logging.INFO)
        
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            log_dir = os.path.join(base_dir, 'logs')
            os.makedirs(log_dir, exist_ok=True)
            
            debug_log_path = os.path.join(log_dir, 'debug.log')
            file_handler = logging.FileHandler(debug_log_path)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception:
            # If we can't create log file, continue with console only
            pass
    
    return logger