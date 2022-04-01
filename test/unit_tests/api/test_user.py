from http import HTTPStatus

from orchestrator.utils.json import json_dumps

from company.db import UserPreferenceDomain

USER_NAME = "j.doe@example.com"
DOMAIN = UserPreferenceDomain.NW_DASHBOARD.name
PREF = {"onboarding": True}


def _set_user_preferences(test_client):
    body = {"preferences": PREF}
    response = test_client.put(
        f"/api/surf/user/preferences/{DOMAIN}/{USER_NAME}",
        json=json_dumps(body),
    )
    assert response.status_code == HTTPStatus.NO_CONTENT


def test_get_user_preference(test_client):
    #  set needs to be executed first, otherwise user not found
    _set_user_preferences(test_client)
    response = test_client.get(f"/api/surf/user/preferences/{DOMAIN}/{USER_NAME}")
    assert response.status_code == HTTPStatus.OK


def test_error(test_client):
    response = test_client.post("/api/user/error", data='{"error":"msg"}', headers={"Content-Type": "application/json"})

    assert response.status_code == HTTPStatus.OK


def test_user_info(test_client):
    response = test_client.post(
        "/api/user/log/fredje", data='{"message":"User logged in"}', headers={"Content-Type": "application/json"}
    )
    assert response.status_code == HTTPStatus.OK


def test_user_info_non_valid_json(test_client):
    response = test_client.post(
        "/api/user/log/fredje", data="No valid json", headers={"Content-Type": "application/json"}
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
