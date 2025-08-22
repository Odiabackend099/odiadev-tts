#!/usr/bin/env python3
"""
MANUS AGENT: Comprehensive TTS API Testing
Test both local and deployed versions
"""

import requests
import json
import time
import sys

class TTSAPITester:
    def __init__(self, base_url="https://manus-agent-tts.onrender.com"):
        self.base_url = base_url.rstrip('/')
        self.api_key = "my_key"  # Default test key
        
    def test_endpoint(self, endpoint, method='GET', **kwargs):
        """Test a single endpoint"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == 'GET':
                response = requests.get(url, timeout=30, **kwargs)
            else:
                response = requests.post(url, timeout=60, **kwargs)
            
            return {
                'success': True,
                'status_code': response.status_code,
                'response': response.json() if 'application/json' in response.headers.get('content-type', '') else f"{len(response.content)} bytes",
                'headers': dict(response.headers)
            }
        except requests.exceptions.Timeout:
            return {'success': False, 'error': 'Request timeout'}
        except requests.exceptions.ConnectionError:
            return {'success': False, 'error': 'Connection failed'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def run_comprehensive_test(self):
        """Run all tests"""
        print("🤖 MANUS AGENT: Comprehensive TTS API Testing")
        print("=" * 60)
        print(f"Testing: {self.base_url}")
        print("=" * 60)
        
        tests = [
            {
                'name': 'Health Check',
                'endpoint': '/health',
                'expected_status': 200,
                'critical': True
            },
            {
                'name': 'Real Diagnosis',
                'endpoint': '/manus/diagnose',
                'expected_status': 200,
                'critical': True
            },
            {
                'name': 'Quick Test Audio',
                'endpoint': '/test',
                'expected_status': 200,
                'critical': True,
                'check_audio': True
            },
            {
                'name': 'TTS Generation (GET)',
                'endpoint': '/speak',
                'method': 'GET',
                'params': {'text': 'Hello Nigeria!', 'voice': 'female'},
                'headers': {'x-api-key': self.api_key},
                'expected_status': 200,
                'critical': True,
                'check_audio': True
            },
            {
                'name': 'TTS Generation (POST)',
                'endpoint': '/api/speak',
                'method': 'POST',
                'json': {'text': 'Sannu da zuwa Nigeria!', 'voice': 'male'},
                'headers': {'x-api-key': self.api_key, 'Content-Type': 'application/json'},
                'expected_status': 200,
                'critical': True
            },
            {
                'name': 'Invalid API Key Test',
                'endpoint': '/speak',
                'params': {'text': 'Test'},
                'headers': {'x-api-key': 'invalid_key'},
                'expected_status': 401,
                'critical': False
            },
            {
                'name': 'No Text Test',
                'endpoint': '/speak',
                'headers': {'x-api-key': self.api_key},
                'expected_status': 400,
                'critical': False
            }
        ]
        
        results = {'passed': 0, 'failed': 0, 'critical_failures': []}
        
        for i, test in enumerate(tests, 1):
            print(f"\n[{i}] Testing: {test['name']}")
            print("-" * 40)
            
            # Prepare test parameters
            kwargs = {}
            if 'params' in test:
                kwargs['params'] = test['params']
            if 'json' in test:
                kwargs['json'] = test['json']
            if 'headers' in test:
                kwargs['headers'] = test['headers']
            
            # Run test
            result = self.test_endpoint(
                test['endpoint'],
                test.get('method', 'GET'),
                **kwargs
            )
            
            # Evaluate result
            if result['success']:
                status_ok = result['status_code'] == test['expected_status']
                
                if status_ok:
                    print(f"✅ PASS - Status: {result['status_code']}")
                    
                    # Special checks
                    if test.get('check_audio') and isinstance(result['response'], str) and 'bytes' in result['response']:
                        audio_size = int(result['response'].split()[0])
                        if audio_size > 1000:
                            print(f"   🎵 Audio: {audio_size} bytes (Good)")
                        else:
                            print(f"   ⚠️ Audio: {audio_size} bytes (Too small)")
                    
                    if isinstance(result['response'], dict):
                        if 'status' in result['response']:
                            print(f"   Status: {result['response']['status']}")
                        if 'checks' in result['response']:
                            print("   Diagnosis:")
                            for check, status in result['response']['checks'].items():
                                print(f"     {check}: {status}")
                    
                    results['passed'] += 1
                else:
                    print(f"❌ FAIL - Expected {test['expected_status']}, got {result['status_code']}")
                    print(f"   Response: {result['response']}")
                    results['failed'] += 1
                    
                    if test.get('critical'):
                        results['critical_failures'].append(test['name'])
            else:
                print(f"❌ FAIL - {result['error']}")
                results['failed'] += 1
                
                if test.get('critical'):
                    results['critical_failures'].append(test['name'])
        
        # Summary
        print("\n" + "=" * 60)
        print("🏁 TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {results['passed']}")
        print(f"❌ Failed: {results['failed']}")
        
        if results['critical_failures']:
            print(f"🚨 CRITICAL FAILURES: {', '.join(results['critical_failures'])}")
            print("\n🔧 NEXT STEPS:")
            print("1. Check /manus/diagnose endpoint for detailed error analysis")
            print("2. Verify edge-tts is properly installed on Render")
            print("3. Check Render logs for specific error messages")
            return False
        else:
            print("🎉 ALL CRITICAL TESTS PASSED!")
            print("✨ Your TTS API is working correctly!")
            return True

def main():
    # Test both local and deployed
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = "https://manus-agent-tts.onrender.com"
    
    print(f"Testing URL: {url}")
    
    tester = TTSAPITester(url)
    success = tester.run_comprehensive_test()
    
    if not success:
        print("\n💡 TIP: Try testing locally first:")
        print("python test_comprehensive.py http://localhost:5000")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())