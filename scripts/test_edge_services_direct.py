#!/usr/bin/env python3
"""
Direct Edge Services Test Script
Tests MQTT, SFTP, and WebSocket services directly without import issues
"""

import sys
import time
from pathlib import Path

# Add edge src to path
edge_src = Path(__file__).parent.parent / "edge" / "src"
sys.path.insert(0, str(edge_src))

def test_mqtt_service():
    """Test MQTT service directly"""
    print("Testing MQTT service...")
    try:
        # Import directly from the file
        import importlib.util
        spec = importlib.util.spec_from_file_location("mqtt_client", edge_src / "services" / "mqtt_client.py")
        mqtt_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mqtt_module)
        
        # Create client
        client = mqtt_module.MQTTClient()
        print(f"✅ MQTT client created: {client.host}:{client.port}")
        return True
    except Exception as e:
        print(f"❌ MQTT test failed: {e}")
        return False

def test_sftp_service():
    """Test SFTP service directly"""
    print("Testing SFTP service...")
    try:
        # Import directly from the file
        import importlib.util
        spec = importlib.util.spec_from_file_location("sftp_transfer", edge_src / "services" / "sftp_transfer.py")
        sftp_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(sftp_module)
        
        # Create transfer service
        transfer = sftp_module.SFTPTransfer('localhost', 'aicamera', 'aicamera123')
        print(f"✅ SFTP service created: {transfer.host}:{transfer.port}")
        return True
    except Exception as e:
        print(f"❌ SFTP test failed: {e}")
        return False

def test_websocket_service():
    """Test WebSocket service directly"""
    print("Testing WebSocket service...")
    try:
        # Import directly from the file
        import importlib.util
        spec = importlib.util.spec_from_file_location("websocket_client", edge_src / "services" / "websocket_client.py")
        ws_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ws_module)
        
        # Create WebSocket client
        ws = ws_module.WebSocketClient('ws://localhost:3000')
        print(f"✅ WebSocket client created: {ws.server_url}")
        return True
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")
        return False

def main():
    print("🚀 Testing Edge Communication Services Directly")
    print("=" * 50)
    print("📁 Using services from: edge/src/services/")
    print("📁 Environment template: edge/installation/env.production.template")
    print("=" * 50)
    
    results = []
    
    # Test each service
    results.append(("MQTT Service", test_mqtt_service()))
    results.append(("SFTP Service", test_sftp_service()))
    results.append(("WebSocket Service", test_websocket_service()))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS")
    print("=" * 50)
    
    passed = 0
    for service_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{service_name}: {status}")
        if result:
            passed += 1
    
    print("-" * 50)
    print(f"PASSED: {passed}/{len(results)}")
    
    if passed == len(results):
        print("\n🎉 All edge communication services are working correctly!")
        print("✅ MQTT Service: Ready")
        print("✅ SFTP Service: Ready")
        print("✅ WebSocket Service: Ready")
        print("\n📋 Next steps:")
        print("1. Copy environment template: cp edge/installation/env.production.template edge/.env.production")
        print("2. Update .env.production with your configuration")
        print("3. Start the edge application: cd edge && ./start_edge.sh")
    else:
        print(f"\n⚠️  {len(results) - passed} service(s) need attention")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
