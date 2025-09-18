#!/usr/bin/env python3
"""Test script for appointment endpoints."""

import asyncio
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add the backend directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

import httpx
from app.core.config import settings


async def test_appointment_endpoints():
    """Test the appointment CRUD endpoints."""
    
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        print("Testing Secre API Appointment Endpoints")
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
        
        # Test creating an appointment
        print("\n2. Testing appointment creation...")
        try:
            # Create appointment for tomorrow
            start_time = datetime.utcnow() + timedelta(days=1, hours=10)
            end_time = start_time + timedelta(hours=1)
            
            appointment_data = {
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
                "notification_state": "PENDING",
                "appointment_type": "CONSULTATION",
                "clinic_id": "CLINIC001",
                "comment": "Consulta de seguimiento",
                "customFields": {
                    "room_number": "A-101",
                    "specialty": "Cardiología",
                    "priority": "Normal",
                    "equipment_needed": ["ECG", "Blood pressure monitor"],
                    "notes": "Patient prefers morning appointments"
                }
            }
            
            response = await client.post(f"{base_url}/v1/appointments/", json=appointment_data, headers=headers)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 201:
                appointment = response.json()
                appointment_id = appointment['id']
                print(f"   ✓ Appointment created: {appointment['id']}")
                print(f"   ✓ Start: {appointment['start_utc']}")
                print(f"   ✓ End: {appointment['end_utc']}")
                print(f"   ✓ Patient: {appointment['patient_document_number']}")
                print(f"   ✓ Doctor: {appointment['doctor_document_number']}")
                print(f"   ✓ Custom fields: {len(appointment['custom_fields'])} fields")
            else:
                print(f"   ✗ Creation failed: {response.text}")
                return
        except Exception as e:
            print(f"   ✗ Creation error: {e}")
            return
        
        # Test getting the appointment
        print("\n3. Testing appointment retrieval...")
        try:
            response = await client.get(f"{base_url}/v1/appointments/{appointment_id}", headers=headers)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                appointment = response.json()
                print(f"   ✓ Appointment retrieved: {appointment['id']}")
                print(f"   ✓ State: {appointment['state']}")
                print(f"   ✓ Modality: {appointment['modality']}")
                print(f"   ✓ Custom fields: {appointment['custom_fields']}")
            else:
                print(f"   ✗ Retrieval failed: {response.text}")
        except Exception as e:
            print(f"   ✗ Retrieval error: {e}")
        
        # Test updating the appointment
        print("\n4. Testing appointment update...")
        try:
            update_data = {
                "eventType": "APPOINTMENT",
                "actionType": "UPDATE",
                "state": "CONFIRMED",
                "notification_state": "SENT",
                "customFields": {
                    "room_number": "A-102",
                    "specialty": "Cardiología",
                    "priority": "High",
                    "equipment_needed": ["ECG", "Blood pressure monitor", "Echocardiogram"],
                    "notes": "Patient confirmed, prefers morning appointments",
                    "insurance_verified": True,
                    "copay_amount": 5000
                }
            }
            
            response = await client.patch(f"{base_url}/v1/appointments/{appointment_id}", json=update_data, headers=headers)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                appointment = response.json()
                print(f"   ✓ Appointment updated: {appointment['state']}")
                print(f"   ✓ Notification state: {appointment['notification_state']}")
                print(f"   ✓ Updated custom fields: {appointment['custom_fields']}")
            else:
                print(f"   ✗ Update failed: {response.text}")
        except Exception as e:
            print(f"   ✗ Update error: {e}")
        
        # Test searching appointments
        print("\n5. Testing appointment search...")
        try:
            # Search by patient document number
            response = await client.get(
                f"{base_url}/v1/appointments/?patient_document_number=12345678",
                headers=headers
            )
            print(f"   Search by patient - Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✓ Found {data['total']} appointments for patient")
                if data['appointments']:
                    appointment = data['appointments'][0]
                    print(f"   ✓ Appointment: {appointment['id']} - {appointment['state']}")
            
            # Search by state
            response = await client.get(
                f"{base_url}/v1/appointments/?state=CONFIRMED",
                headers=headers
            )
            print(f"   Search by state - Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✓ Found {data['total']} confirmed appointments")
            
            # Search by modality
            response = await client.get(
                f"{base_url}/v1/appointments/?modality=IN_PERSON",
                headers=headers
            )
            print(f"   Search by modality - Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✓ Found {data['total']} in-person appointments")
            
        except Exception as e:
            print(f"   ✗ Search error: {e}")
        
        # Test creating another appointment
        print("\n6. Testing second appointment creation...")
        try:
            # Create appointment for next week
            start_time2 = datetime.utcnow() + timedelta(days=7, hours=14)
            end_time2 = start_time2 + timedelta(hours=2)
            
            appointment2_data = {
                "eventType": "APPOINTMENT",
                "actionType": "CREATE",
                "startAppointment": start_time2.isoformat() + "Z",
                "endAppointment": end_time2.isoformat() + "Z",
                "patient_document_type_id": 1,
                "patient_document_number": "87654321",
                "doctor_document_type_id": 1,
                "doctor_document_number": "12345678",
                "modality": "VIRTUAL",
                "state": "SCHEDULED",
                "appointment_type": "FOLLOW_UP",
                "clinic_id": "CLINIC002",
                "comment": "Seguimiento virtual",
                "customFields": {
                    "platform": "Zoom",
                    "meeting_link": "https://zoom.us/j/123456789",
                    "specialty": "Medicina General",
                    "priority": "Normal",
                    "preparation_notes": "Patient should have blood work results ready"
                }
            }
            
            response = await client.post(f"{base_url}/v1/appointments/", json=appointment2_data, headers=headers)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 201:
                appointment2 = response.json()
                appointment2_id = appointment2['id']
                print(f"   ✓ Second appointment created: {appointment2['id']}")
                print(f"   ✓ Modality: {appointment2['modality']}")
                print(f"   ✓ Type: {appointment2['appointment_type']}")
            else:
                print(f"   ✗ Second appointment creation failed: {response.text}")
        except Exception as e:
            print(f"   ✗ Second appointment creation error: {e}")
        
        # Test date range search
        print("\n7. Testing date range search...")
        try:
            # Search appointments in the next 10 days
            start_date = datetime.utcnow()
            end_date = start_date + timedelta(days=10)
            
            response = await client.get(
                f"{base_url}/v1/appointments/by-date-range?start_date={start_date.isoformat()}Z&end_date={end_date.isoformat()}Z",
                headers=headers
            )
            print(f"   Date range search - Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✓ Found {data['total']} appointments in date range")
                for appointment in data['appointments']:
                    print(f"   - {appointment['id']}: {appointment['start_utc']} ({appointment['state']})")
            else:
                print(f"   ✗ Date range search failed: {response.text}")
        except Exception as e:
            print(f"   ✗ Date range search error: {e}")
        
        # Test listing all appointments
        print("\n8. Testing appointment listing...")
        try:
            response = await client.get(f"{base_url}/v1/appointments/", headers=headers)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✓ Found {data['total']} appointments total")
                print(f"   ✓ Page {data['page']} of {data['total_pages'] if 'total_pages' in data else '?'}")
                print(f"   ✓ Has next: {data['has_next']}, Has prev: {data['has_prev']}")
                
                for i, appointment in enumerate(data['appointments'], 1):
                    print(f"   {i}. {appointment['id']}: {appointment['start_utc']} - {appointment['state']} ({appointment['modality']})")
            else:
                print(f"   ✗ Listing failed: {response.text}")
        except Exception as e:
            print(f"   ✗ Listing error: {e}")
        
        # Test deleting an appointment
        print("\n9. Testing appointment deletion...")
        try:
            response = await client.delete(f"{base_url}/v1/appointments/{appointment2_id}", headers=headers)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✓ Appointment {appointment2_id} deleted successfully")
            else:
                print(f"   ✗ Deletion failed: {response.text}")
        except Exception as e:
            print(f"   ✗ Deletion error: {e}")
        
        # Verify deletion
        print("\n10. Verifying deletion...")
        try:
            response = await client.get(f"{base_url}/v1/appointments/{appointment2_id}", headers=headers)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 404:
                print(f"   ✓ Appointment {appointment2_id} confirmed deleted")
            else:
                print(f"   ✗ Appointment still exists: {response.text}")
        except Exception as e:
            print(f"   ✗ Verification error: {e}")
        
        # Test time validation
        print("\n11. Testing time validation...")
        try:
            # Try to create appointment with end time before start time
            invalid_appointment = {
                "eventType": "APPOINTMENT",
                "actionType": "CREATE",
                "startAppointment": end_time.isoformat() + "Z",
                "endAppointment": start_time.isoformat() + "Z",  # End before start
                "patient_document_type_id": 1,
                "patient_document_number": "99999999",
                "doctor_document_type_id": 1,
                "doctor_document_number": "11111111",
                "modality": "IN_PERSON",
                "state": "SCHEDULED"
            }
            
            response = await client.post(f"{base_url}/v1/appointments/", json=invalid_appointment, headers=headers)
            print(f"   Invalid time validation - Status: {response.status_code}")
            
            if response.status_code == 400:
                print(f"   ✓ Time validation working: {response.json().get('detail', 'Unknown error')}")
            else:
                print(f"   ✗ Time validation failed: {response.text}")
        except Exception as e:
            print(f"   ✗ Time validation error: {e}")
        
        print("\n" + "=" * 50)
        print("Appointment endpoints test completed!")


if __name__ == "__main__":
    asyncio.run(test_appointment_endpoints())
