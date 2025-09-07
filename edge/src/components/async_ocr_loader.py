#!/usr/bin/env python3
"""
Asynchronous OCR Loader for AI Camera v1.3

This module provides asynchronous loading of EasyOCR to prevent blocking
the main application startup sequence. EasyOCR initialization can take
6-10 seconds, which causes health endpoint timeouts during system startup.

Features:
- Asynchronous EasyOCR Reader initialization
- Thread-safe OCR operations with fallback
- Status monitoring and progress tracking
- Graceful degradation when OCR is not ready
- Timeout handling and retry logic

Author: AI Camera Team
Version: 1.3
Date: August 2025
"""

import threading
import time
import logging
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, Future

from edge.src.core.utils.logging_config import get_logger
from edge.src.core.config import EASYOCR_LANGUAGES

logger = get_logger(__name__)


class AsyncOCRLoader:
    """
    Asynchronous OCR Loader for non-blocking EasyOCR initialization.
    
    This class manages the asynchronous loading of EasyOCR Reader to prevent
    blocking the main application startup. It provides thread-safe access
    to OCR functionality with proper fallback handling.
    """
    
    def __init__(self, languages: List[str] = None, logger: logging.Logger = None):
        """
        Initialize Async OCR Loader.
        
        Args:
            languages: List of languages for EasyOCR (defaults to config)
            logger: Logger instance
        """
        self.logger = logger or get_logger(__name__)
        self.languages = languages or EASYOCR_LANGUAGES
        
        # OCR Reader state
        self._ocr_reader: Optional[Any] = None
        self._loading_future: Optional[Future] = None
        self._is_loading = False
        self._is_ready = False
        self._load_error: Optional[Exception] = None
        self._load_start_time: Optional[datetime] = None
        self._load_end_time: Optional[datetime] = None
        
        # Thread safety
        self._lock = threading.RLock()
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="OCR-Loader")
        
        # Statistics
        self.stats = {
            'initialization_attempts': 0,
            'initialization_time': 0.0,
            'ocr_requests': 0,
            'successful_ocr': 0,
            'failed_ocr': 0,
            'fallback_used': 0
        }
        
        self.logger.info("AsyncOCRLoader initialized")
    
    def start_loading(self) -> bool:
        """
        Start asynchronous OCR Reader loading.
        
        Returns:
            bool: True if loading started, False if already loading/loaded
        """
        with self._lock:
            if self._is_loading or self._is_ready:
                self.logger.debug("OCR loading already in progress or complete")
                return False
            
            self._is_loading = True
            self._load_start_time = datetime.now()
            self.stats['initialization_attempts'] += 1
            
            # Submit loading task to thread pool
            self._loading_future = self._executor.submit(self._load_ocr_reader)
            
            self.logger.info("🚀 Started asynchronous EasyOCR loading...")
            return True
    
    def _load_ocr_reader(self) -> bool:
        """
        Internal method to load EasyOCR Reader (runs in background thread).
        
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        try:
            self.logger.info(f"Loading EasyOCR Reader with languages: {self.languages}")
            
            # Import and initialize EasyOCR
            # Patch sympy to handle missing equal_valued function
            try:
                import sympy.core.numbers
                if not hasattr(sympy.core.numbers, 'equal_valued'):
                    def equal_valued(a, b):
                        return a == b
                    sympy.core.numbers.equal_valued = equal_valued
            except ImportError:
                pass
            
            import easyocr
            start_time = time.time()
            
            # This is the blocking call that takes ~6-10 seconds
            reader = easyocr.Reader(self.languages)
            
            end_time = time.time()
            load_time = end_time - start_time
            
            # Update state with successful loading
            with self._lock:
                self._ocr_reader = reader
                self._is_ready = True
                self._is_loading = False
                self._load_end_time = datetime.now()
                self.stats['initialization_time'] = load_time
            
            self.logger.info(f"✅ EasyOCR loaded successfully in {load_time:.2f} seconds")
            return True
            
        except Exception as e:
            # Update state with error
            with self._lock:
                self._load_error = e
                self._is_loading = False
                self._load_end_time = datetime.now()
            
            self.logger.error(f"❌ Failed to load EasyOCR: {e}")
            return False
    
    def is_ready(self) -> bool:
        """
        Check if OCR Reader is ready for use.
        
        Returns:
            bool: True if OCR Reader is loaded and ready
        """
        with self._lock:
            return self._is_ready and self._ocr_reader is not None
    
    def is_loading(self) -> bool:
        """
        Check if OCR Reader is currently loading.
        
        Returns:
            bool: True if loading is in progress
        """
        with self._lock:
            return self._is_loading
    
    def get_loading_status(self) -> Dict[str, Any]:
        """
        Get detailed loading status information.
        
        Returns:
            Dict containing loading status, timing, and error information
        """
        with self._lock:
            status = {
                'is_ready': self._is_ready,
                'is_loading': self._is_loading,
                'has_error': self._load_error is not None,
                'error_message': str(self._load_error) if self._load_error else None,
                'load_start_time': self._load_start_time.isoformat() if self._load_start_time else None,
                'load_end_time': self._load_end_time.isoformat() if self._load_end_time else None,
                'languages': self.languages,
                'stats': self.stats.copy()
            }
            
            # Calculate loading duration if applicable
            if self._load_start_time:
                end_time = self._load_end_time or datetime.now()
                duration = (end_time - self._load_start_time).total_seconds()
                status['loading_duration'] = duration
            
            return status
    
    def wait_for_ready(self, timeout: float = 30.0) -> bool:
        """
        Wait for OCR Reader to be ready with timeout.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            bool: True if ready within timeout, False otherwise
        """
        if self.is_ready():
            return True
        
        if not self.is_loading():
            self.logger.warning("OCR not loading - starting load first")
            if not self.start_loading():
                return False
        
        # Wait for completion with timeout
        start_wait = time.time()
        while time.time() - start_wait < timeout:
            if self.is_ready():
                return True
            
            if not self.is_loading():
                # Loading finished but not ready - must have failed
                break
                
            time.sleep(0.1)
        
        self.logger.warning(f"OCR not ready after {timeout}s timeout")
        return False
    
    def read_text(self, image, detail: int = 0, paragraph: bool = False, 
                  width_ths: float = 0.7, height_ths: float = 0.7,
                  **kwargs) -> List[Tuple]:
        """
        Perform OCR text reading with fallback handling.
        
        Args:
            image: Input image (numpy array)
            detail: Detail level (0=text only, 1=text+confidence)
            paragraph: Enable paragraph detection
            width_ths: Width threshold for text detection
            height_ths: Height threshold for text detection
            **kwargs: Additional arguments for EasyOCR
            
        Returns:
            List[Tuple]: OCR results or empty list if not ready
        """
        self.stats['ocr_requests'] += 1
        
        if not self.is_ready():
            self.logger.debug("OCR not ready - cannot perform text reading")
            self.stats['fallback_used'] += 1
            return []
        
        try:
            with self._lock:
                if self._ocr_reader is None:
                    self.logger.warning("OCR Reader is None despite being marked as ready")
                    self.stats['failed_ocr'] += 1
                    return []
                
                # Perform OCR reading
                results = self._ocr_reader.readtext(
                    image, 
                    detail=detail,
                    paragraph=paragraph,
                    width_ths=width_ths,
                    height_ths=height_ths,
                    **kwargs
                )
                
                self.stats['successful_ocr'] += 1
                return results
                
        except Exception as e:
            self.logger.error(f"OCR reading failed: {e}")
            self.stats['failed_ocr'] += 1
            return []
    
    def cleanup(self):
        """Clean up resources and shutdown thread pool."""
        try:
            if self._loading_future and not self._loading_future.done():
                self.logger.info("Cancelling OCR loading task...")
                self._loading_future.cancel()
            
            self._executor.shutdown(wait=True)
            self.logger.info("AsyncOCRLoader cleaned up")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    def __del__(self):
        """Destructor to ensure cleanup."""
        try:
            self.cleanup()
        except:
            pass  # Ignore errors during destruction


# Global singleton instance
_global_ocr_loader: Optional[AsyncOCRLoader] = None
_global_lock = threading.Lock()


def get_async_ocr_loader() -> AsyncOCRLoader:
    """
    Get the global AsyncOCRLoader singleton instance.
    
    Returns:
        AsyncOCRLoader: Global OCR loader instance
    """
    global _global_ocr_loader
    
    with _global_lock:
        if _global_ocr_loader is None:
            _global_ocr_loader = AsyncOCRLoader()
        return _global_ocr_loader


def start_global_ocr_loading() -> bool:
    """
    Start loading the global OCR loader.
    
    Returns:
        bool: True if loading started successfully
    """
    loader = get_async_ocr_loader()
    return loader.start_loading()
