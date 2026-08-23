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
    assert test_user_id not in dbApplication.doctor_selected_room


if __name__ == "__main__":
    test_admin_clinic_room_crud()
    print("✅ All admin clinic room tests passed successfully!")
