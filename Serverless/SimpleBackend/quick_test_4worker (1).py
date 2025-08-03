#!/usr/bin/env python3
"""Quick test of 4-worker endpoint"""
import requests

url = 'https://api.runpod.ai/v2/rqwaizbda7ucsj/runsync'
headers = {
    'Authorization': 'Bearer rpa_G4713KLVTYYBJYWPO157LX7VVPGV7NZ2K87SX6B17otl1t', 
    'Content-Type': 'application/json'
}

print('🔍 Testing 4-worker endpoint...')
try:
    r = requests.post(url, headers=headers, json={'input': {'type': 'health'}}, timeout=15)
    print(f'Status: {r.status_code}')
    if r.status_code == 200:
        result = r.json()
        output = result.get('output', {})
        print(f'Health: {output.get("status", "unknown")}')
        print('✅ Endpoint działa!')
    else:
        print(f'Response: {r.text[:100]}')
except Exception as e:
    print(f'Error: {e}')