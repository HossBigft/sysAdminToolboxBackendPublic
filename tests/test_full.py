from fastapi.testclient import TestClient
from app.main import app
from .test_data.data_command_injection_list import COMMAND_INJECTION_LIST
from .test_data.sql_injection_lists import (
    AUTH_BYPASS_SQL_QUERY_LIST,
    GENERIC_INJECTION_SQL_QUERY_LIST,
    GENERIC_ERRORBASED_SQL_QUERY_LIST,
    GENERIC_TIMEBASED_INJECTION_SQL_QUERY_LIST,
)

import pytest
client = TestClient(app)


@pytest.mark.parametrize("command", COMMAND_INJECTION_LIST)
def test_invalid_commands_trigger_422_error(command):
    response = client.get(f"/get/zonemaster/?domain={command}")
    assert response.status_code == 422


@pytest.mark.parametrize("injection_query", AUTH_BYPASS_SQL_QUERY_LIST)
def test_subscription_query_against_authentification_bypass_sql_injection(
    injection_query,
):
    response = client.get(f"/plesk/get/subscription/?domain={injection_query}")
    assert response.status_code == 422


@pytest.mark.parametrize("injection_query", GENERIC_INJECTION_SQL_QUERY_LIST)
def test_subscription_query_against_generic_sql_injection(injection_query):
    response = client.get(f"/plesk/get/subscription/?domain={injection_query}")
    assert response.status_code == 422


@pytest.mark.parametrize("injection_query", GENERIC_ERRORBASED_SQL_QUERY_LIST)
def test_subscription_query_against_generic_errorbased_sql_injection(injection_query):
    response = client.get(f"/plesk/get/subscription/?domain={injection_query}")
    assert response.status_code == 422


@pytest.mark.parametrize("injection_query", GENERIC_TIMEBASED_INJECTION_SQL_QUERY_LIST)
def test_subscription_query_against_generic_timebased_sql_injection(injection_query):
    response = client.get(f"/plesk/get/subscription/?domain={injection_query}")
    assert response.status_code == 422
