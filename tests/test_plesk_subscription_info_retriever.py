import pytest
from app.ssh_plesk_subscription_info_retriever import (
    is_valid_domain,
    build_query,
    parse_answer,
)
from tests.test_data.hosts import HostList


def test_valid_domain(domain=HostList.CORRECT_EXISTING_SUBDOMAIN):
    assert is_valid_domain(domain)


invalid_domains = [
    "ex",  # Too short
    "example..com",  # Double dot
    "-example.com",  # Leading dash
    "example.com-",  # Trailing dash
    "example.com.",  # Trailing dot
    "example@com",  # Invalid character '@'
    "IP_PLACEHOLDER",  # Not a domain
    "invalid_domain",  # Invalid format
    "example.c",  # Top-level domain too short
    "a" * 64 + ".com",  # Too long (64 characters)
    HostList.MALFORMED_DOMAIN,
]


@pytest.mark.parametrize("domain", invalid_domains)
def test_invalid_domain(domain):
    assert not is_valid_domain(domain)


def test_query_builder(domain=HostList.CORRECT_EXISTING_DOMAIN):
    correct_query = (
        "SELECT CASE WHEN webspace_id = 0 THEN id ELSE webspace_id END AS result "
        "FROM domains WHERE name LIKE '{0}'; "
        "SELECT name FROM domains WHERE id=(SELECT CASE WHEN webspace_id = 0 THEN id ELSE webspace_id END AS result FROM domains WHERE name LIKE '{0}'); "
        "SELECT pname, login FROM clients WHERE id=(SELECT cl_id FROM domains WHERE name LIKE '{0}'); "
        "SELECT name FROM domains WHERE webspace_id=(SELECT CASE WHEN webspace_id = 0 THEN id ELSE webspace_id END AS result FROM domains WHERE name LIKE '{0}');"
    ).format(domain)

    assert build_query(domain) == correct_query


def test_parse_answer():
    sample_input = {
        "host": "example.com",
        "stdout": "12345\nTest Name\nuser1\tlogin1\ndomain1.com\ndomain2.com",
    }

    expected_output = {
        "host": "example.com",
        "id": "12345",
        "name": "Test Name",
        "username": "user1",
        "userlogin": "login1",
        "domains": ["domain1.com", "domain2.com"],
    }

    result = parse_answer(sample_input)

    assert result == expected_output


def test_parse_answer_empty_stdout():
    sample_input = {"host": "example.com", "stdout": "\n\n\n\n"}

    result = parse_answer(sample_input)
    assert result is None


def test_parse_correct_answer():
    sample_input = {
        "host": "pleskserver.",
        "stdout": """
        1187
google.com
        FIO\tp-2342343
google.com
google.com
google.com
google.com
google.com
google.com
google.com
google.com
google.com
        """,
    }

    expected_output = {
        "host": "pleskserver.",
        "id": "1187",
google.com
        "username": "FIO",
        "userlogin": "p-2342343",
        "domains": [
google.com
google.com
google.com
google.com
google.com
google.com
google.com
google.com
google.com
        ],
    }

    result = parse_answer(sample_input)

    assert result == expected_output
