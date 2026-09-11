from tests.conftest import auth_headers, login_user, register_user
from tests.test_prescriptions import prescription_payload


async def test_users_cannot_access_each_others_data(client, user_payload):
    first_user_headers = await register_and_authenticate(client, user_payload)
    created = await client.post(
        "/prescriptions",
        json=prescription_payload(),
        headers=first_user_headers,
    )
    prescription_id = created.json()["id"]
    patient_id = created.json()["patient"]["id"]

    second_payload = {
        **user_payload,
        "username": "another-owner",
        "email": "another-owner@example.com",
    }
    second_user_headers = await register_and_authenticate(client, second_payload)

    patient_response = await client.get(
        f"/patients/{patient_id}", headers=second_user_headers
    )
    prescription_response = await client.get(
        f"/prescriptions/{prescription_id}", headers=second_user_headers
    )
    reuse_response = await client.post(
        "/prescriptions",
        json={
            "patient_id": patient_id,
            "prescription": {
                "prescribed_at": "2026-09-12T10:00:00Z",
                "sphere_od": -1,
            },
        },
        headers=second_user_headers,
    )

    assert patient_response.status_code == 404
    assert prescription_response.status_code == 404
    assert reuse_response.status_code == 404


async def register_and_authenticate(client, payload):
    await register_user(client, payload)
    token = await login_user(client, payload["username"], payload["password"])
    return auth_headers(token)
