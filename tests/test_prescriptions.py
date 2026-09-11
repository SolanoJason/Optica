from tests.conftest import auth_headers, login_user, register_user


def prescription_payload(full_name: str = "Jane Doe") -> dict:
    return {
        "patient": {"full_name": full_name, "phone_number": "555-0100"},
        "prescription": {
            "prescribed_at": "2026-09-11T10:00:00Z",
            "sphere_od": "-1.25",
            "cylinder_od": "-0.50",
            "axis_od": 90,
        },
    }


async def authenticated_client(client, user_payload):
    await register_user(client, user_payload)
    token = await login_user(client, user_payload["username"], user_payload["password"])
    return auth_headers(token)


async def test_prescription_creates_patient(client, user_payload):
    headers = await authenticated_client(client, user_payload)

    response = await client.post(
        "/prescriptions",
        json=prescription_payload(),
        headers=headers,
    )

    assert response.status_code == 201
    body = response.json()
    assert body["patient"]["full_name"] == "Jane Doe"
    assert body["sphere_od"] == -1.25

    patients = await client.get("/patients", headers=headers)
    assert patients.status_code == 200
    assert len(patients.json()) == 1


async def test_existing_patient_can_receive_another_prescription(client, user_payload):
    headers = await authenticated_client(client, user_payload)
    first = await client.post(
        "/prescriptions", json=prescription_payload(), headers=headers
    )
    patient_id = first.json()["patient"]["id"]

    second = await client.post(
        "/prescriptions",
        json={
            "patient_id": patient_id,
            "prescription": {
                "prescribed_at": "2026-09-12T10:00:00Z",
                "sphere_os": "-2.00",
            },
        },
        headers=headers,
    )

    assert second.status_code == 201
    assert second.json()["patient"]["id"] == patient_id

    prescriptions = await client.get("/prescriptions", headers=headers)
    assert len(prescriptions.json()) == 2


async def test_patient_and_prescription_filters(client, user_payload):
    headers = await authenticated_client(client, user_payload)
    await client.post(
        "/prescriptions", json=prescription_payload("Jane Doe"), headers=headers
    )
    await client.post(
        "/prescriptions",
        json=prescription_payload("John Smith")
        | {"prescription": {"prescribed_at": "2026-10-01T10:00:00Z", "pd_od": 62}},
        headers=headers,
    )

    patients = await client.get("/patients?q=jane", headers=headers)
    assert [patient["full_name"] for patient in patients.json()] == ["Jane Doe"]

    prescriptions = await client.get(
        "/prescriptions?q=john&prescribed_after=2026-09-30T00:00:00Z",
        headers=headers,
    )
    assert len(prescriptions.json()) == 1
    assert prescriptions.json()[0]["patient"]["full_name"] == "John Smith"


async def test_invalid_prescription_returns_validation_error(client, user_payload):
    headers = await authenticated_client(client, user_payload)
    payload = prescription_payload()
    payload["prescription"] = {"prescribed_at": "2026-09-11T10:00:00Z"}

    response = await client.post("/prescriptions", json=payload, headers=headers)

    assert response.status_code == 422
