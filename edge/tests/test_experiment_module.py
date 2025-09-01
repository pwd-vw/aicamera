# test_experiment_module.py
#!/usr/bin/env python3
"""ทดสอบ Experiment Module"""

import sys
import os
from pathlib import Path
# เพิ่ม path ของ edge/src เข้าไปใน Python path (เหมือนกับที่ app.py ทำ)
current_dir = Path(__file__).parent
src_dir = current_dir.parent / 'src'
sys.path.insert(0, str(src_dir))

from core.dependency_container import get_container

def test_experiment_services():
    """ทดสอบการลงทะเบียนและใช้งาน Experiment services"""
    try:
        print("�� Testing Experiment Module...")
        print(f"   - Current working directory: {os.getcwd()}")
        print(f"   - Python path: {sys.path[:3]}...")

        container = get_container()
        print("✅ Dependency container initialized")

        # ตรวจสอบว่า experiment services ลงทะเบียนแล้ว
        if not container.has_service('experiment_isolator'):
            print("❌ Experiment Isolator not registered")
            return False
            
        if not container.has_service('experiment_service'):
            print("❌ Experiment Service not registered")
            return False
        print("✅ Experiment services registered successfully")

        # ดึง services
        try:
            isolator = container.get_service('experiment_isolator')
            print(f"   - Isolator: {type(isolator).__name__}")
        except Exception as e:
            print(f"❌ Error getting isolator: {e}")
            return False
        
        try:
            experiment_service = container.get_service('experiment_service')
            print(f"   - Service: {type(experiment_service).__name__}")
        except Exception as e:
            print(f"❌ Error getting experiment service: {e}")
            return False
        
        print("✅ Experiment services registered successfully")
        print(f"   - Isolator: {type(isolator).__name__}")
        print(f"   - Service: {type(experiment_service).__name__}")
        
         # ทดสอบการทำงานของ isolator
        try:
            status = isolator.get_experiment_status()
            print(f"   - Isolator status: {status}")
        except Exception as e:
            print(f"⚠️  Warning getting isolator status: {e}")
        
        # ทดสอบการทำงานของ experiment service
        try:
            exp_status = experiment_service.get_experiment_status()
            print(f"   - Experiment service status: {exp_status}")
        except Exception as e:
            print(f"⚠️  Warning getting experiment status: {e}")
        
        # ทดสอบการดึงรายการการทดลอง
        try:
            available_experiments = experiment_service.get_available_experiments()
            print(f"   - Available experiments: {len(available_experiments)}")
            for exp in available_experiments:
                print(f"     * {exp['name']}: {exp['type']}")
        except Exception as e:
            print(f"⚠️  Warning getting available experiments: {e}")
        
        print("✅ All tests completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error testing experiment services: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_experiment_services()
    sys.exit(0 if success else 1)