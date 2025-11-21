#!/usr/bin/env python3
"""
Focus Mode Testing Script for AI Camera

This script allows you to test different focus modes independently
without restarting the main service.

Usage:
    python edge/src/tools/test_focus_modes.py --mode continuous --duration 300
    python edge/src/tools/test_focus_modes.py --mode auto --duration 300 --trigger-interval 30
    python edge/src/tools/test_focus_modes.py --compare-all --duration 300

Author: AI Camera Team
Version: 2.0
Date: December 2025
"""

import sys
import os
import argparse
import time
import signal
from pathlib import Path

# Determine project root - handle both direct execution and module execution
if __file__:
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent.parent
else:
    # Fallback if __file__ is not available
    project_root = Path.cwd()

# Set PYTHONPATH environment variable
pythonpath = os.environ.get('PYTHONPATH', '')
if str(project_root) not in pythonpath:
    if pythonpath:
        os.environ['PYTHONPATH'] = f"{project_root}:{pythonpath}"
    else:
        os.environ['PYTHONPATH'] = str(project_root)

# Add project root to sys.path
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Change to project root directory for proper imports
original_cwd = os.getcwd()
try:
    os.chdir(project_root)
except Exception:
    pass

# Now import modules
try:
    from edge.src.core.dependency_container import get_service
    from edge.src.core.utils.logging_config import get_logger
    from edge.src.components.enhanced_focus_controller import EnhancedFocusController
    from edge.src.components.focus_test_framework import FocusTestFramework
except ImportError as e:
    # Fallback: try adding edge/src to path
    edge_src = project_root / 'edge' / 'src'
    if str(edge_src) not in sys.path:
        sys.path.insert(0, str(edge_src))
    
    try:
        from core.dependency_container import get_service
        from core.utils.logging_config import get_logger
        from components.enhanced_focus_controller import EnhancedFocusController
        from components.focus_test_framework import FocusTestFramework
    except ImportError as e2:
        print(f"Error: Failed to import required modules.")
        print(f"Project root: {project_root}")
        print(f"Python path: {sys.path}")
        print(f"Import error: {e}")
        print(f"Fallback import error: {e2}")
        print("\nPlease ensure you are running from the project root directory.")
        print("Or set PYTHONPATH: export PYTHONPATH=$PWD:$PYTHONPATH")
        sys.exit(1)

logger = get_logger(__name__)


class FocusTestRunner:
    """Standalone focus test runner."""
    
    def __init__(self, service_name='aicamera_lpr'):
        """
        Initialize test runner.
        
        Args:
            service_name: Systemd service name (default: aicamera_lpr)
        """
        self.camera_handler = None
        self.detection_manager = None
        self.test_framework = None
        self.running = True
        self.service_name = service_name
        self.service_was_running = False
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle interrupt signals."""
        logger.info("Received interrupt signal, shutting down gracefully...")
        self.running = False
        # Ensure cleanup happens
        self.cleanup()
        sys.exit(1)
    
    def _check_service_status(self) -> bool:
        """
        Check if service is running.
        
        Returns:
            bool: True if service is running, False otherwise
        """
        try:
            import subprocess
            result = subprocess.run(
                ['systemctl', 'is-active', '--quiet', self.service_name],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception as e:
            logger.warning(f"Failed to check service status: {e}")
            return False
    
    def _stop_service(self) -> bool:
        """
        Stop the camera service.
        
        Returns:
            bool: True if service was stopped successfully
        """
        try:
            import subprocess
            
            # Check if service is running
            if not self._check_service_status():
                logger.info(f"Service {self.service_name} is not running.")
                return True
            
            logger.info(f"Stopping service {self.service_name}...")
            result = subprocess.run(
                ['sudo', 'systemctl', 'stop', self.service_name],
                capture_output=True,
                timeout=30,
                text=True
            )
            
            if result.returncode == 0:
                # Wait for service to fully stop
                logger.info("Waiting for service to stop...")
                for i in range(30):  # Wait up to 3 seconds
                    if not self._check_service_status():
                        logger.info(f"Service {self.service_name} stopped successfully.")
                        self.service_was_running = True
                        return True
                    time.sleep(0.1)
                
                logger.warning("Service stop timeout, but continuing...")
                self.service_was_running = True
                return True
            else:
                logger.error(f"Failed to stop service: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Service stop command timed out")
            return False
        except Exception as e:
            logger.error(f"Error stopping service: {e}")
            return False
    
    def _start_service(self) -> bool:
        """
        Start the camera service.
        
        Returns:
            bool: True if service was started successfully
        """
        if not self.service_was_running:
            logger.info(f"Service {self.service_name} was not running before test, skipping start.")
            return True
        
        try:
            import subprocess
            
            logger.info(f"Starting service {self.service_name}...")
            result = subprocess.run(
                ['sudo', 'systemctl', 'start', self.service_name],
                capture_output=True,
                timeout=30,
                text=True
            )
            
            if result.returncode == 0:
                # Wait for service to fully start
                logger.info("Waiting for service to start...")
                for i in range(60):  # Wait up to 6 seconds
                    if self._check_service_status():
                        logger.info(f"Service {self.service_name} started successfully.")
                        return True
                    time.sleep(0.1)
                
                logger.warning("Service start timeout, but service may be starting...")
                return True
            else:
                logger.error(f"Failed to start service: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Service start command timed out")
            return False
        except Exception as e:
            logger.error(f"Error starting service: {e}")
            return False
    
    def initialize_services(self, skip_service_control=False):
        """
        Initialize camera and detection services.
        
        Args:
            skip_service_control: If True, skip service stop/start (service should already be stopped)
        """
        try:
            logger.info("Initializing services...")
            
            # Stop main service first (camera doesn't support multi-access)
            # Note: Service should already be stopped by main() if not skipped
            if not skip_service_control:
                if not self._stop_service():
                    logger.error("Failed to stop main service. Cannot proceed with test.")
                    return False
                
                # Wait a bit for service to fully release camera
                logger.info("Waiting for camera to be released...")
                time.sleep(2)
            
            # Get camera handler from dependency container
            camera_manager = get_service('camera_manager')
            if not camera_manager:
                logger.error("Camera manager not available. Make sure the service is running.")
                return False
            
            self.camera_handler = camera_manager.camera_handler
            if not self.camera_handler:
                logger.error("Camera handler not available.")
                return False
            
            # Check if camera is initialized and streaming
            if not self.camera_handler.initialized:
                logger.warning("Camera not initialized. Attempting to initialize...")
                if not self.camera_handler.initialize_camera():
                    logger.error("Failed to initialize camera.")
                    return False
            
            if not self.camera_handler.streaming:
                logger.warning("Camera not streaming. Attempting to start...")
                if not self.camera_handler.start_camera():
                    logger.error("Failed to start camera.")
                    return False
            
            # Configure camera for IMX708 LPR use case (optimized for vehicles approaching camera)
            if self.camera_handler.picam2:
                try:
                    # Log camera properties
                    camera_props = self.camera_handler.camera_properties
                    logger.info(f"Camera Model: {camera_props.get('Model', 'Unknown')}")
                    logger.info(f"Pixel Array: {camera_props.get('PixelArrayActiveAreas', 'Unknown')}")
                    
                    # Apply optimal configuration for IMX708 LPR use case
                    # For vehicles approaching camera, use continuous autofocus with center-weighted metering
                    lpr_config = {
                        "AfMode": 2,  # Continuous autofocus (best for moving objects)
                        "AfSpeed": 0,  # Normal speed (0=Normal, 1=Fast)
                        "AfMetering": 1,  # Center-weighted metering (best for LPR)
                        "AfRange": 0,  # Full range (0=Full, 1=Macro, 2=Normal)
                        "Brightness": 0.0,  # Default brightness
                        "Contrast": 1.0,  # Normal contrast
                        "Saturation": 1.0,  # Normal saturation
                        "Sharpness": 1.0,  # Normal sharpness
                        "AeEnable": True,  # Auto exposure
                        "AwbEnable": True,  # Auto white balance
                    }
                    
                    # Try to use libcamera controls if available
                    try:
                        from libcamera import controls as lc_controls
                        lpr_config["AwbMode"] = lc_controls.AwbModeEnum.Auto
                        lpr_config["AeConstraintMode"] = lc_controls.AeConstraintModeEnum.Normal
                        logger.info("Using libcamera controls for enhanced configuration")
                    except ImportError:
                        logger.debug("libcamera controls not available, using basic controls")
                    
                    self.camera_handler.picam2.set_controls(lpr_config)
                    logger.info("IMX708 LPR configuration applied: Continuous AF, Center-weighted, Normal speed")
                    
                    # Log current configuration
                    current_config = self.camera_handler.current_config
                    if current_config:
                        main_size = current_config.get('main', {}).get('size', 'Unknown')
                        lores_size = current_config.get('lores', {}).get('size', 'Unknown')
                        logger.info(f"Stream configuration - Main: {main_size}, Lores: {lores_size}")
                    
                except Exception as e:
                    logger.warning(f"Failed to apply IMX708 LPR configuration: {e}")
            
            # Wait for frame buffer to be ready
            logger.info("Waiting for frame buffer to be ready...")
            for i in range(30):  # Wait up to 3 seconds
                if self.camera_handler.is_frame_buffer_ready():
                    break
                time.sleep(0.1)
            else:
                logger.warning("Frame buffer not ready, but continuing...")
            
            # Get detection manager (optional)
            try:
                self.detection_manager = get_service('detection_manager')
                if self.detection_manager:
                    logger.info("Detection manager available.")
                else:
                    logger.warning("Detection manager not available. Tests will run without detection.")
            except Exception as e:
                logger.warning(f"Detection manager not available: {e}")
            
            # Initialize test framework
            self.test_framework = FocusTestFramework(
                self.camera_handler,
                self.detection_manager
            )
            
            logger.info("Services initialized successfully.")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize services: {e}")
            return False
    
    def run_single_test(self, mode: str, duration: int, **kwargs):
        """
        Run a single focus mode test.
        
        Args:
            mode: Focus mode ("auto", "continuous", "manual", "hybrid")
            duration: Test duration in seconds
            **kwargs: Mode-specific parameters
        """
        if not self.test_framework:
            logger.error("Test framework not initialized.")
            return None
        
        logger.info(f"Starting test: mode={mode}, duration={duration}s")
        
        try:
            result = self.test_framework.run_test(mode, duration, **kwargs)
            
            if result:
                logger.info("Test completed successfully.")
                logger.info(f"  Focus Quality - Mean: {result.get('focus_quality', {}).get('mean', 0):.1f}")
                logger.info(f"  Detection Rate: {result.get('detection_metrics', {}).get('detection_rate', 0):.3f}")
                logger.info(f"  Total Frames: {result.get('total_frames', 0)}")
            else:
                logger.error("Test failed or returned no results.")
            
            return result
            
        except Exception as e:
            logger.error(f"Test failed: {e}")
            return None
    
    def run_comparison_test(self, duration: int = 300):
        """
        Run tests for all modes and compare results.
        
        Args:
            duration: Test duration for each mode in seconds
        """
        if not self.test_framework:
            logger.error("Test framework not initialized.")
            return None
        
        logger.info(f"Running comparison test for all modes (duration: {duration}s each)")
        
        # Recommended modes for IMX708 LPR use case (vehicles approaching camera)
        modes_to_test = [
            ("continuous", {"speed": 0, "metering": 1, "range_mode": 0}),  # Best for LPR - continuous tracking
            ("auto", {"trigger_interval": 30.0, "poor_threshold": 400}),  # Good for stable scenarios
            ("hybrid", {"base_distance": 3.0, "continuous_range": 2.0}),  # Adaptive focus
            ("manual", {"distance_m": 3.0, "unlock_interval": 60.0})  # Fixed focus for fixed distance
        ]
        
        results = {}
        
        for mode, params in modes_to_test:
            if not self.running:
                logger.info("Test interrupted by user.")
                break
            
            logger.info(f"\n{'='*60}")
            logger.info(f"Testing mode: {mode}")
            logger.info(f"{'='*60}")
            
            result = self.run_single_test(mode, duration, **params)
            if result:
                results[mode] = result
            
            # Wait between tests
            if mode != modes_to_test[-1][0]:  # Not the last mode
                logger.info("Waiting 10 seconds before next test...")
                time.sleep(10)
        
        # Compare results
        if results:
            logger.info(f"\n{'='*60}")
            logger.info("Comparing results...")
            logger.info(f"{'='*60}")
            
            comparison = self.test_framework.compare_results()
            
            if comparison:
                logger.info(f"\nBest Mode: {comparison.get('best_mode', {}).get('mode', 'N/A')}")
                logger.info(f"Best Score: {comparison.get('best_mode', {}).get('score', 0):.3f}")
                
                logger.info("\nOverall Scores:")
                for mode, score_data in comparison.get('overall_scores', {}).items():
                    logger.info(f"  {mode}: {score_data['score']:.3f} ({', '.join(score_data['factors'])})")
                
                logger.info("\nFocus Quality Comparison:")
                for mode, fq_data in comparison.get('focus_quality_comparison', {}).items():
                    logger.info(f"  {mode}:")
                    logger.info(f"    Mean FocusFoM: {fq_data['mean']:.1f}")
                    logger.info(f"    Excellent: {fq_data['excellent_percent']:.1f}%")
                    logger.info(f"    Poor: {fq_data['poor_percent']:.1f}%")
                
                logger.info("\nDetection Comparison:")
                for mode, dc_data in comparison.get('detection_comparison', {}).items():
                    logger.info(f"  {mode}:")
                    logger.info(f"    Detection Rate: {dc_data['detection_rate']:.3f}")
                    logger.info(f"    Total Vehicles: {dc_data['total_vehicles']}")
                    logger.info(f"    Total Plates: {dc_data['total_plates']}")
                
                # Export results
                try:
                    output_file = self.test_framework.export_results()
                    logger.info(f"\nResults exported to: {output_file}")
                except Exception as e:
                    logger.error(f"Failed to export results: {e}")
                    # Try to export to home directory as fallback
                    import os
                    home_dir = os.path.expanduser("~")
                    fallback_path = os.path.join(home_dir, "aicamera_test_results.json")
                    try:
                        output_file = self.test_framework.export_results(fallback_path)
                        logger.info(f"Results exported to fallback location: {output_file}")
                    except Exception as e2:
                        logger.error(f"Failed to export to fallback location: {e2}")
                
                return comparison
        
        return None
    
    def cleanup(self):
        """Cleanup resources."""
        logger.info("Cleaning up...")
        
        # Stop camera properly
        if self.camera_handler:
            try:
                logger.info("Stopping camera...")
                if self.camera_handler.streaming:
                    self.camera_handler.stop_camera()
                    logger.info("Camera stopped.")
                
                # Wait for camera to fully release
                time.sleep(1)
                
                # Close camera to ensure complete release
                if self.camera_handler.initialized:
                    self.camera_handler.close_camera()
                    logger.info("Camera closed.")
            except Exception as e:
                logger.warning(f"Error stopping camera: {e}")
        
        # Wait a bit before starting service
        logger.info("Waiting before restarting service...")
        time.sleep(2)
        
        # Restart main service
        if self.service_was_running:
            logger.info("Restarting main service...")
            self._start_service()
        else:
            logger.info("Service was not running before test, not restarting.")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Test different focus modes for AI Camera',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test continuous mode for 5 minutes
  python edge/src/tools/test_focus_modes.py --mode continuous --duration 300
  
  # Test auto mode with custom parameters
  python edge/src/tools/test_focus_modes.py --mode auto --duration 300 --trigger-interval 30
  
  # Test all modes and compare
  python edge/src/tools/test_focus_modes.py --compare-all --duration 300
  
  # Test manual mode with specific distance
  python edge/src/tools/test_focus_modes.py --mode manual --duration 300 --distance 3.0
        """
    )
    
    parser.add_argument(
        '--mode',
        choices=['auto', 'continuous', 'manual', 'hybrid'],
        help='Focus mode to test'
    )
    
    parser.add_argument(
        '--compare-all',
        action='store_true',
        help='Test all modes and compare results'
    )
    
    parser.add_argument(
        '--duration',
        type=int,
        default=300,
        help='Test duration in seconds (default: 300)'
    )
    
    # Auto mode parameters
    parser.add_argument(
        '--trigger-interval',
        type=float,
        default=30.0,
        help='Auto mode: Trigger interval in seconds (default: 30.0)'
    )
    
    parser.add_argument(
        '--poor-threshold',
        type=int,
        default=400,
        help='Auto mode: Poor focus threshold (default: 400)'
    )
    
    # Continuous mode parameters
    parser.add_argument(
        '--speed',
        type=int,
        choices=[0, 1],
        default=0,
        help='Continuous mode: Focus speed (0=Normal, 1=Fast, default: 0)'
    )
    
    parser.add_argument(
        '--metering',
        type=int,
        choices=[0, 1],
        default=1,
        help='Continuous mode: Metering mode (0=Auto, 1=Center, default: 1)'
    )
    
    # Manual mode parameters
    parser.add_argument(
        '--distance',
        type=float,
        default=3.0,
        help='Manual mode: Focus distance in meters (default: 3.0)'
    )
    
    parser.add_argument(
        '--unlock-interval',
        type=float,
        default=60.0,
        help='Manual mode: Unlock interval in seconds (default: 60.0)'
    )
    
    # Hybrid mode parameters
    parser.add_argument(
        '--base-distance',
        type=float,
        default=3.0,
        help='Hybrid mode: Base distance in meters (default: 3.0)'
    )
    
    parser.add_argument(
        '--continuous-range',
        type=float,
        default=2.0,
        help='Hybrid mode: Continuous range in meters (default: 2.0)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        help='Output file path for results (optional)'
    )
    
    parser.add_argument(
        '--service-name',
        type=str,
        default='aicamera_lpr',
        help='Systemd service name (default: aicamera_lpr)'
    )
    
    parser.add_argument(
        '--skip-service-control',
        action='store_true',
        help='Skip stopping/starting service (use with caution - camera may be busy)'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.compare_all and not args.mode:
        parser.error("Either --mode or --compare-all must be specified")
    
    # Initialize test runner
    runner = FocusTestRunner(service_name=args.service_name)
    
    # Skip service control if requested
    if args.skip_service_control:
        logger.warning("Skipping service control - camera may be busy if service is running!")
        runner.service_was_running = False  # Don't restart if we didn't stop
    
    try:
        # Stop main service first (camera doesn't support multi-access)
        if not args.skip_service_control:
            if not runner._stop_service():
                logger.error("Failed to stop main service. Use --skip-service-control if service is not running.")
                sys.exit(1)
            time.sleep(2)  # Wait for camera to be released
        
        # Initialize services (service should already be stopped if not skipped)
        if not runner.initialize_services(skip_service_control=args.skip_service_control):
            logger.error("Failed to initialize services. Exiting.")
            sys.exit(1)
        
        # Run test
        if args.compare_all:
            # Run comparison test
            comparison = runner.run_comparison_test(duration=args.duration)
            
            if comparison and args.output:
                runner.test_framework.export_results(args.output)
        else:
            # Run single mode test
            mode_params = {}
            
            if args.mode == 'auto':
                mode_params = {
                    'trigger_interval': args.trigger_interval,
                    'poor_threshold': args.poor_threshold
                }
            elif args.mode == 'continuous':
                mode_params = {
                    'speed': args.speed,
                    'metering': args.metering,
                    'range_mode': 0
                }
            elif args.mode == 'manual':
                mode_params = {
                    'distance_m': args.distance,
                    'unlock_interval': args.unlock_interval
                }
            elif args.mode == 'hybrid':
                mode_params = {
                    'base_distance': args.base_distance,
                    'continuous_range': args.continuous_range
                }
            
            result = runner.run_single_test(
                args.mode,
                args.duration,
                **mode_params
            )
            
            if result and args.output:
                try:
                    runner.test_framework.export_results(args.output)
                except Exception as e:
                    logger.error(f"Failed to export results to {args.output}: {e}")
                    # Try default location
                    try:
                        output_file = runner.test_framework.export_results()
                        logger.info(f"Results exported to default location: {output_file}")
                    except Exception as e2:
                        logger.error(f"Failed to export results: {e2}")
        
        logger.info("\nTest completed successfully!")
        
    except KeyboardInterrupt:
        logger.info("\nTest interrupted by user.")
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        sys.exit(1)
    finally:
        runner.cleanup()


if __name__ == '__main__':
    main()

