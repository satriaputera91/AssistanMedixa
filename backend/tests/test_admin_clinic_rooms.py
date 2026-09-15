import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parents[1]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.core.database import dbApplication
from app.modules.admin.schemas import (
    ClinicRoomAdminView,
    CreateClinicRoomRequest,
    UpdateClinicRoomRequest,
)


def test_admin_clinic_room_crud():
    # 1. Check initial room count
    initial_count = len(dbApplication.clinic_rooms)
    assert initial_count >= 9

    # 2. Test create clinic room
    create_req = CreateClinicRoomRequest(
        room_name="Poli Rehabilitasi Medik",
        room_code="REHAB-01",
        floor="Lantai 1",
        building="Gedung C",
        specialty="Physical Medicine and Rehabilitation",
        status="active",
        operational_hours="08:00 - 15:00 WIB",
        description="Layanan fisioterapi dan pemulihan fisik pasien.",
    )

    created_room = dbApplication.create_clinic_room(create_req.model_dump())
    assert created_room is not None
    room_id = created_room["room_id"]
    assert created_room["room_name"] == "Poli Rehabilitasi Medik"
    assert created_room["room_code"] == "REHAB-01"
    assert created_room["status"] == "active"
    assert len(dbApplication.clinic_rooms) == initial_count + 1

    # 3. Test duplicate room code prevention
    try:
        dbApplication.create_clinic_room(create_req.model_dump())
        assert False, "Should have raised ValueError on duplicate room_code"
    except ValueError as e:
        assert "sudah digunakan" in str(e)

    # 4. Test get all rooms (enriched with assigned doctors)
    all_rooms = dbApplication.get_all_clinic_rooms()
    assert len(all_rooms) == len(dbApplication.clinic_rooms)
    found = next((r for r in all_rooms if r["room_id"] == room_id), None)
    assert found is not None
    assert "assigned_doctors" in found
    assert isinstance(found["assigned_doctors"], list)

    # 5. Test update clinic room
    update_data = {
        "room_name": "Poli Rehabilitasi Medik & Fisioterapi",
        "floor": "Lantai 2",
        "operational_hours": "07:30 - 16:00 WIB",
    }
    updated_room = dbApplication.update_clinic_room(room_id, update_data)
    assert updated_room is not None
    assert updated_room["room_name"] == "Poli Rehabilitasi Medik & Fisioterapi"
    assert updated_room["floor"] == "Lantai 2"
    assert updated_room["operational_hours"] == "07:30 - 16:00 WIB"

    # 6. Test toggle status
    toggled = dbApplication.toggle_clinic_room_status(room_id)
    assert toggled["status"] == "inactive"
    toggled_again = dbApplication.toggle_clinic_room_status(room_id)
    assert toggled_again["status"] == "active"

    # 7. Test doctor assignment & deletion unassignment
    # Simulate a doctor assigned to this room
    test_user_id = "u1"
    dbApplication.doctor_selected_room[test_user_id] = room_id
    room_with_doc = dbApplication.get_clinic_room(room_id)
    assert len(room_with_doc["assigned_doctors"]) == 1
    assert room_with_doc["assigned_doctors"][0]["id"] == test_user_id

    # 8. Test delete clinic room
    del_ok = dbApplication.delete_clinic_room(room_id)
    assert del_ok is True
    assert dbApplication.get_clinic_room(room_id) is None
    # Verify doctor was unassigned
def test_doctor_logout_and_login_resets_selected_room():
    from fastapi.testclient import TestClient
    from app.main import app
    
    client = TestClient(app)
    
    # 1. Login doctor
    login_res = client.post("/api/v1/auth/login", json={"email": "doctor@AssistantMedixa.com", "password": "doctor123"})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    user_id = login_res.json()["user_id"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Select a clinic room
    select_res = client.post("/api/v1/agent/clinic-rooms/select", json={"room_id": "ROOM-001"}, headers=headers)
    assert select_res.status_code == 200
    assert select_res.json()["selected_room"]["room_id"] == "ROOM-001"
    assert dbApplication.doctor_selected_room.get(user_id) == "ROOM-001"
    
    # 3. Doctor logs out -> Room selection must be reset
    logout_res = client.post("/api/v1/auth/logout", headers=headers)
    assert logout_res.status_code == 200
    assert user_id not in dbApplication.doctor_selected_room
    
    # 4. Check selected room returns None
    get_res = client.get("/api/v1/agent/clinic-rooms/selected", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["selected_room"] is None
    
    # 5. Doctor logs in again -> Fresh session requires room selection
    login_res2 = client.post("/api/v1/auth/login", json={"email": "doctor@AssistantMedixa.com", "password": "doctor123"})
    assert login_res2.status_code == 200
    token2 = login_res2.json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}
    
    get_res2 = client.get("/api/v1/agent/clinic-rooms/selected", headers=headers2)
    assert get_res2.status_code == 200
    assert get_res2.json()["selected_room"] is None, "New login must require doctor to select clinic room again"


if __name__ == "__main__":
    test_admin_clinic_room_crud()
    test_doctor_logout_and_login_resets_selected_room()
    print("✅ All admin clinic room and logout reset tests passed successfully!")
