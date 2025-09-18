#!/usr/bin/env python3
"""Test script for patient endpoints."""

import asyncio
import sys
from datetime import date
from pathlib import Path

# Add the backend directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

import httpx
from app.core.config import settings


async def test_patient_endpoints():
    """Test the patient CRUD endpoints."""
    
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        print("Testing Secre API Patient Endpoints")
        print("=" * 50)
        
        # First, bootstrap the system to get an API key
        print("\n1. Bootstrapping system...")
        try:
            bootstrap_data = {
                "name": "Test Medical Center"
            }
            response = await client.post(f"{base_url}/v1/admin/bootstrap", json=bootstrap_data)
            if response.status_code == 201:
                data = response.json()
                api_key = data['plaintext_key']
                tenant_id = data['api_key']['tenant_id']
                print(f"   ✓ System bootstrapped")
                print(f"   ✓ API Key: {api_key[:8]}...")
                print(f"   ✓ Tenant ID: {tenant_id}")
            else:
                print(f"   ✗ Bootstrap failed: {response.status_code} - {response.text}")
                return
        except Exception as e:
            print(f"   ✗ Bootstrap error: {e}")
            return
        
        headers = {"X-Api-Key": api_key}
        
        # Test creating a patient
        print("\n2. Testing patient creation...")
        try:
            patient_data = {
                "eventType": "PATIENT",
                "actionType": "CREATE",
                "first_name": "Juan Carlos",
                "first_last_name": "Pérez",
                "second_last_name": "García",
                "birth_date": "1985-05-15",
                "gender_id": 1,
                "document_type_id": 1,
                "document_number": "12345678",
                "email": "juan.perez@example.com",
                "phone": "+57-1-234-5678",
                "cell_phone": "+57-300-123-4567",
                "eps_id": "EPS001",
                "habeas_data": True,
                "customFields": {
                    "emergency_contact": "María Pérez - +57-300-987-6543",
                    "allergies": ["Penicilina", "Polen"],
                    "medical_conditions": ["Hipertensión"],
                    "blood_type": "O+",
                    "insurance_number": "INS-123456"
                }
            }
            
            response = await client.post(f"{base_url}/v1/patients/", json=patient_data, headers=headers)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 201:
                patient = response.json()
                patient_id = patient['id']
                print(f"   ✓ Patient created: {patient['first_name']} {patient['first_last_name']}")
                print(f"   ✓ Patient ID: {patient_id}")
                print(f"   ✓ Document: {patient['document_number']}")
                print(f"   ✓ Custom fields: {len(patient['custom_fields'])} fields")
            else:
                print(f"   ✗ Creation failed: {response.text}")
                return
        except Exception as e:
            print(f"   ✗ Creation error: {e}")
            return
        
        # Test getting the patient
        print("\n3. Testing patient retrieval...")
        try:
            response = await client.get(f"{base_url}/v1/patients/{patient_id}", headers=headers)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                patient = response.json()
                print(f"   ✓ Patient retrieved: {patient['first_name']} {patient['first_last_name']}")
                print(f"   ✓ Email: {patient['email']}")
                print(f"   ✓ Custom fields: {patient['custom_fields']}")
            else:
                print(f"   ✗ Retrieval failed: {response.text}")
        except Exception as e:
            print(f"   ✗ Retrieval error: {e}")
        
        # Test updating the patient
        print("\n4. Testing patient update...")
        try:
            update_data = {
                "eventType": "PATIENT",
                "actionType": "UPDATE",
                "email": "juan.perez.updated@example.com",
                "customFields": {
                    "emergency_contact": "María Pérez - +57-300-987-6543",
                    "allergies": ["Penicilina", "Polen", "Aspirina"],
                    "medical_conditions": ["Hipertensión", "Diabetes"],
                    "blood_type": "O+",
                    "insurance_number": "INS-123456",
                    "preferred_language": "Spanish"
                }
            }
            
            response = await client.patch(f"{base_url}/v1/patients/{patient_id}", json=update_data, headers=headers)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                patient = response.json()
                print(f"   ✓ Patient updated: {patient['email']}")
                print(f"   ✓ Updated custom fields: {patient['custom_fields']}")
            else:
                print(f"   ✗ Update failed: {response.text}")
        except Exception as e:
            print(f"   ✗ Update error: {e}")
        
        # Test searching patients
        print("\n5. Testing patient search...")
        try:
            # Search by document number
            response = await client.get(
                f"{base_url}/v1/patients/?document_number=12345678",
                headers=headers
            )
            print(f"   Search by document - Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✓ Found {data['total']} patients")
                if data['patients']:
                    patient = data['patients'][0]
                    print(f"   ✓ Patient: {patient['first_name']} {patient['first_last_name']}")
            
            # Search by email
            response = await client.get(
                f"{base_url}/v1/patients/?email=juan.perez.updated@example.com",
                headers=headers
            )
            print(f"   Search by email - Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✓ Found {data['total']} patients by email")
            
        except Exception as e:
            print(f"   ✗ Search error: {e}")
        
        # Test creating another patient
        print("\n6. Testing second patient creation...")
        try:
            patient2_data = {
                "eventType": "PATIENT",
                "actionType": "CREATE",
                "first_name": "María Elena",
                "first_last_name": "Rodríguez",
                "birth_date": "1990-08-22",
                "gender_id": 2,
                "document_type_id": 1,
                "document_number": "87654321",
                "email": "maria.rodriguez@example.com",
                "cell_phone": "+57-300-555-1234",
                "eps_id": "EPS002",
                "habeas_data": True,
                "customFields": {
                    "emergency_contact": "Carlos Rodríguez - +57-300-555-5678",
                    "allergies": [],
                    "medical_conditions": [],
                    "blood_type": "A+",
                    "pregnancy_status": "Not pregnant"
                }
            }
            
            response = await client.post(f"{base_url}/v1/patients/", json=patient2_data, headers=headers)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 201:
                patient2 = response.json()
                patient2_id = patient2['id']
                print(f"   ✓ Second patient created: {patient2['first_name']} {patient2['first_last_name']}")
                print(f"   ✓ Patient ID: {patient2_id}")
            else:
                print(f"   ✗ Second patient creation failed: {response.text}")
        except Exception as e:
            print(f"   ✗ Second patient creation error: {e}")
        
        # Test listing all patients
        print("\n7. Testing patient listing...")
        try:
            response = await client.get(f"{base_url}/v1/patients/", headers=headers)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✓ Found {data['total']} patients total")
                print(f"   ✓ Page {data['page']} of {data['total_pages'] if 'total_pages' in data else '?'}")
                print(f"   ✓ Has next: {data['has_next']}, Has prev: {data['has_prev']}")
                
                for i, patient in enumerate(data['patients'], 1):
                    print(f"   {i}. {patient['first_name']} {patient['first_last_name']} ({patient['document_number']})")
            else:
                print(f"   ✗ Listing failed: {response.text}")
        except Exception as e:
            print(f"   ✗ Listing error: {e}")
        
        # Test deleting a patient
        print("\n8. Testing patient deletion...")
        try:
            response = await client.delete(f"{base_url}/v1/patients/{patient2_id}", headers=headers)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✓ Patient {patient2_id} deleted successfully")
            else:
                print(f"   ✗ Deletion failed: {response.text}")
        except Exception as e:
            print(f"   ✗ Deletion error: {e}")
        
        # Verify deletion
        print("\n9. Verifying deletion...")
        try:
            response = await client.get(f"{base_url}/v1/patients/{patient2_id}", headers=headers)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 404:
                print(f"   ✓ Patient {patient2_id} confirmed deleted")
            else:
                print(f"   ✗ Patient still exists: {response.text}")
        except Exception as e:
            print(f"   ✗ Verification error: {e}")
        
        print("\n" + "=" * 50)
        print("Patient endpoints test completed!")


if __name__ == "__main__":
    asyncio.run(test_patient_endpoints())
