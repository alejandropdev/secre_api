#!/usr/bin/env python3
"""Test script for validation and normalization features."""

import asyncio
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

# Add the backend directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

import httpx
from app.core.config import settings


async def test_validation_features():
    """Test the validation and normalization features."""
    
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        print("Testing Secre API Validation and Normalization")
        print("=" * 60)
        
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
                print(f"   ✓ System bootstrapped")
                print(f"   ✓ API Key: {api_key[:8]}...")
            else:
                print(f"   ✗ Bootstrap failed: {response.status_code} - {response.text}")
                return
        except Exception as e:
            print(f"   ✗ Bootstrap error: {e}")
            return
        
        headers = {"X-Api-Key": api_key}
        
        # Test valid patient data
        print("\n2. Testing valid patient data...")
        try:
            valid_patient = {
                "eventType": "PATIENT",
                "actionType": "CREATE",
                "first_name": "Juan Carlos",
                "first_last_name": "Pérez",
                "birth_date": "1985-05-15",
                "gender_id": 1,
                "document_type_id": 1,
                "document_number": "12345678",
                "email": "juan.perez@example.com",
                "phone": "+57-300-123-4567",
                "cell_phone": "300-555-1234",
                "customFields": {
                    "emergency_contact": "María Pérez",
                    "allergies": ["Penicilina"],
                    "medical_conditions": ["Hipertensión"]
                }
            }
            
            response = await client.post(f"{base_url}/v1/patients/", json=valid_patient, headers=headers)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 201:
                patient = response.json()
                print(f"   ✓ Valid patient created: {patient['first_name']} {patient['first_last_name']}")
                print(f"   ✓ Normalized phone: {patient['phone']}")
                print(f"   ✓ Normalized cell phone: {patient['cell_phone']}")
                print(f"   ✓ Normalized email: {patient['email']}")
                print(f"   ✓ Normalized document: {patient['document_number']}")
            else:
                print(f"   ✗ Valid patient creation failed: {response.text}")
        except Exception as e:
            print(f"   ✗ Valid patient creation error: {e}")
        
        # Test invalid document number
        print("\n3. Testing invalid document number...")
        try:
            invalid_doc_patient = {
                "eventType": "PATIENT",
                "actionType": "CREATE",
                "first_name": "Test",
                "first_last_name": "User",
                "birth_date": "1990-01-01",
                "gender_id": 1,
                "document_type_id": 1,
                "document_number": "invalid-doc",  # Invalid format
                "email": "test@example.com"
            }
            
            response = await client.post(f"{base_url}/v1/patients/", json=invalid_doc_patient, headers=headers)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 422:
                print(f"   ✓ Invalid document number properly rejected")
                print(f"   ✓ Validation error: {response.json()}")
            else:
                print(f"   ✗ Invalid document number should have been rejected: {response.text}")
        except Exception as e:
            print(f"   ✗ Invalid document test error: {e}")
        
        # Test invalid email
        print("\n4. Testing invalid email...")
        try:
            invalid_email_patient = {
                "eventType": "PATIENT",
                "actionType": "CREATE",
                "first_name": "Test",
                "first_last_name": "User",
                "birth_date": "1990-01-01",
                "gender_id": 1,
                "document_type_id": 1,
                "document_number": "87654321",
                "email": "invalid-email"  # Invalid format
            }
            
            response = await client.post(f"{base_url}/v1/patients/", json=invalid_email_patient, headers=headers)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 422:
                print(f"   ✓ Invalid email properly rejected")
                print(f"   ✓ Validation error: {response.json()}")
            else:
                print(f"   ✗ Invalid email should have been rejected: {response.text}")
        except Exception as e:
            print(f"   ✗ Invalid email test error: {e}")
        
        # Test invalid phone number
        print("\n5. Testing invalid phone number...")
        try:
            invalid_phone_patient = {
                "eventType": "PATIENT",
                "actionType": "CREATE",
                "first_name": "Test",
                "first_last_name": "User",
                "birth_date": "1990-01-01",
                "gender_id": 1,
                "document_type_id": 1,
                "document_number": "11111111",
                "phone": "invalid-phone"  # Invalid format
            }
            
            response = await client.post(f"{base_url}/v1/patients/", json=invalid_phone_patient, headers=headers)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 422:
                print(f"   ✓ Invalid phone properly rejected")
                print(f"   ✓ Validation error: {response.json()}")
            else:
                print(f"   ✗ Invalid phone should have been rejected: {response.text}")
        except Exception as e:
            print(f"   ✗ Invalid phone test error: {e}")
        
        # Test future birth date
        print("\n6. Testing future birth date...")
        try:
            future_birth_patient = {
                "eventType": "PATIENT",
                "actionType": "CREATE",
                "first_name": "Test",
                "first_last_name": "User",
                "birth_date": "2030-01-01",  # Future date
                "gender_id": 1,
                "document_type_id": 1,
                "document_number": "22222222",
                "email": "test@example.com"
            }
            
            response = await client.post(f"{base_url}/v1/patients/", json=future_birth_patient, headers=headers)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 422:
                print(f"   ✓ Future birth date properly rejected")
                print(f"   ✓ Validation error: {response.json()}")
            else:
                print(f"   ✗ Future birth date should have been rejected: {response.text}")
        except Exception as e:
            print(f"   ✗ Future birth date test error: {e}")
        
        # Test valid appointment data
        print("\n7. Testing valid appointment data...")
        try:
            start_time = datetime.utcnow() + timedelta(days=1, hours=10)
            end_time = start_time + timedelta(hours=1)
            
            valid_appointment = {
                "eventType": "APPOINTMENT",
                "actionType": "CREATE",
                "startAppointment": start_time.isoformat() + "Z",
                "endAppointment": end_time.isoformat() + "Z",
                "patient_document_type_id": 1,
                "patient_document_number": "12345678",
                "doctor_document_type_id": 1,
                "doctor_document_number": "87654321",
                "modality": "IN_PERSON",
                "state": "SCHEDULED",
                "customFields": {
                    "room_number": "A-101",
                    "specialty": "Cardiología",
                    "equipment_needed": ["ECG", "Blood pressure monitor"]
                }
            }
            
            response = await client.post(f"{base_url}/v1/appointments/", json=valid_appointment, headers=headers)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 201:
                appointment = response.json()
                print(f"   ✓ Valid appointment created: {appointment['id']}")
                print(f"   ✓ Start time: {appointment['start_utc']}")
                print(f"   ✓ End time: {appointment['end_utc']}")
                print(f"   ✓ Custom fields: {appointment['custom_fields']}")
            else:
                print(f"   ✗ Valid appointment creation failed: {response.text}")
        except Exception as e:
            print(f"   ✗ Valid appointment creation error: {e}")
        
        # Test invalid appointment time (end before start)
        print("\n8. Testing invalid appointment time...")
        try:
            start_time = datetime.utcnow() + timedelta(days=1, hours=10)
            end_time = start_time - timedelta(hours=1)  # End before start
            
            invalid_time_appointment = {
                "eventType": "APPOINTMENT",
                "actionType": "CREATE",
                "startAppointment": start_time.isoformat() + "Z",
                "endAppointment": end_time.isoformat() + "Z",
                "patient_document_type_id": 1,
                "patient_document_number": "33333333",
                "doctor_document_type_id": 1,
                "doctor_document_number": "11111111",
                "modality": "IN_PERSON",
                "state": "SCHEDULED"
            }
            
            response = await client.post(f"{base_url}/v1/appointments/", json=invalid_time_appointment, headers=headers)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 422:
                print(f"   ✓ Invalid appointment time properly rejected")
                print(f"   ✓ Validation error: {response.json()}")
            else:
                print(f"   ✗ Invalid appointment time should have been rejected: {response.text}")
        except Exception as e:
            print(f"   ✗ Invalid appointment time test error: {e}")
        
        # Test past appointment time
        print("\n9. Testing past appointment time...")
        try:
            start_time = datetime.utcnow() - timedelta(days=1)  # Past time
            end_time = start_time + timedelta(hours=1)
            
            past_appointment = {
                "eventType": "APPOINTMENT",
                "actionType": "CREATE",
                "startAppointment": start_time.isoformat() + "Z",
                "endAppointment": end_time.isoformat() + "Z",
                "patient_document_type_id": 1,
                "patient_document_number": "44444444",
                "doctor_document_type_id": 1,
                "doctor_document_number": "22222222",
                "modality": "IN_PERSON",
                "state": "SCHEDULED"
            }
            
            response = await client.post(f"{base_url}/v1/appointments/", json=past_appointment, headers=headers)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 422:
                print(f"   ✓ Past appointment time properly rejected")
                print(f"   ✓ Validation error: {response.json()}")
            else:
                print(f"   ✗ Past appointment time should have been rejected: {response.text}")
        except Exception as e:
            print(f"   ✗ Past appointment time test error: {e}")
        
        # Test custom fields validation
        print("\n10. Testing custom fields validation...")
        try:
            # Test too many custom fields
            too_many_fields = {f"field_{i}": f"value_{i}" for i in range(60)}  # More than 50
            
            invalid_custom_fields_patient = {
                "eventType": "PATIENT",
                "actionType": "CREATE",
                "first_name": "Test",
                "first_last_name": "User",
                "birth_date": "1990-01-01",
                "gender_id": 1,
                "document_type_id": 1,
                "document_number": "55555555",
                "customFields": too_many_fields
            }
            
            response = await client.post(f"{base_url}/v1/patients/", json=invalid_custom_fields_patient, headers=headers)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 422:
                print(f"   ✓ Too many custom fields properly rejected")
                print(f"   ✓ Validation error: {response.json()}")
            else:
                print(f"   ✗ Too many custom fields should have been rejected: {response.text}")
        except Exception as e:
            print(f"   ✗ Custom fields validation test error: {e}")
        
        # Test phone number normalization
        print("\n11. Testing phone number normalization...")
        try:
            phone_test_patient = {
                "eventType": "PATIENT",
                "actionType": "CREATE",
                "first_name": "Phone",
                "first_last_name": "Test",
                "birth_date": "1990-01-01",
                "gender_id": 1,
                "document_type_id": 1,
                "document_number": "66666666",
                "phone": "300 123 4567",  # Space format
                "cell_phone": "+57-300-555-1234"  # Dash format
            }
            
            response = await client.post(f"{base_url}/v1/patients/", json=phone_test_patient, headers=headers)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 201:
                patient = response.json()
                print(f"   ✓ Phone normalization test passed")
                print(f"   ✓ Original phone: '300 123 4567' -> Normalized: '{patient['phone']}'")
                print(f"   ✓ Original cell: '+57-300-555-1234' -> Normalized: '{patient['cell_phone']}'")
            else:
                print(f"   ✗ Phone normalization test failed: {response.text}")
        except Exception as e:
            print(f"   ✗ Phone normalization test error: {e}")
        
        print("\n" + "=" * 60)
        print("Validation and normalization test completed!")


if __name__ == "__main__":
    asyncio.run(test_validation_features())
