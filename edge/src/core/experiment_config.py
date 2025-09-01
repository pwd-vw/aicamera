# src/config/experiment_config.py
class ExperimentConfig:
    """การตั้งค่า Experiment Module"""
    
    def __init__(self):
        self.enabled = os.getenv('EXPERIMENT_ENABLED', 'true').lower() == 'true'
        self.results_dir = os.getenv('EXPERIMENT_RESULTS_DIR', '/home/camuser/aicamera/experiment_results')
        self.max_concurrent_experiments = int(os.getenv('EXPERIMENT_MAX_CONCURRENT', 1))
        self.auto_save_results = os.getenv('EXPERIMENT_AUTO_SAVE', 'true').lower() == 'true'
        self.max_retention_days = int(os.getenv('EXPERIMENT_MAX_RETENTION', 30))
        
        # Camera configuration presets
        self.camera_presets = {
            'default': {
                'exposure_time': 100000,
                'analog_gain': 1.0,
                'lens_position': 0.0
            },
            'low_light': {
                'exposure_time': 200000,
                'analog_gain': 2.0,
                'lens_position': 0.0
            },
            'high_speed': {
                'exposure_time': 50000,
                'analog_gain': 1.0,
                'lens_position': 0.0
            }
        }
    
    def get_camera_preset(self, preset_name):
        """ดึงการตั้งค่ากล้องตาม preset"""
        return self.camera_presets.get(preset_name, self.camera_presets['default'])
    
    def validate_experiment_config(self, config):
        """ตรวจสอบความถูกต้องของการตั้งค่าการทดลอง"""
        errors = []
        
        if 'experiment_type' not in config:
            errors.append("Missing experiment_type")
        
        if config['experiment_type'] == 'length_detection':
            if 'start_length' not in config or 'max_length' not in config:
                errors.append("Missing length parameters for length detection")
            elif config['start_length'] >= config['max_length']:
                errors.append("start_length must be less than max_length")
        
        return errors