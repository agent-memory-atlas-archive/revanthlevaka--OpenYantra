from openyantra.yantra_security import get_raksha

def test_redact_secrets_openai():
    raksha = get_raksha()
    text = "Here is my key: sk-proj-1234567890abcdef1234567890abcdef for testing."
    cleaned, redactions = raksha.redact_secrets(text)
    assert "sk-proj-1234567890abcdef1234567890abcdef" not in cleaned
    assert "[REDACTED_API_KEY:openai" in cleaned
    assert len(redactions) == 1
    assert redactions[0]["type"] == "openai_api_key"

def test_redact_secrets_anthropic():
    raksha = get_raksha()
    text = "Use this token: sk-ant-api03-abcdef1234567890abcdef123456789012 to connect."
    cleaned, redactions = raksha.redact_secrets(text)
    assert "sk-ant-api03-abcdef1234567890abcdef123456789012" not in cleaned
    assert "[REDACTED_API_KEY:anthropic" in cleaned
    assert len(redactions) == 1
    assert redactions[0]["type"] == "anthropic_api_key"

def test_redact_secrets_github():
    raksha = get_raksha()
    text = "GitHub secret ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
    cleaned, redactions = raksha.redact_secrets(text)
    assert "ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890" not in cleaned
    assert "[REDACTED_API_KEY:github" in cleaned
    assert len(redactions) == 1

def test_redact_secrets_aws():
    raksha = get_raksha()
    text = "AWS access key AKIAIOSFODNN7EXAMPLE deployed on instance."
    cleaned, redactions = raksha.redact_secrets(text)
    assert "AKIAIOSFODNN7EXAMPLE" not in cleaned
    assert "[REDACTED_API_KEY:aws" in cleaned
    assert len(redactions) == 1

def test_redact_secrets_private_key():
    raksha = get_raksha()
    pk = "-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA0Y1...\n-----END RSA PRIVATE KEY-----"
    cleaned, redactions = raksha.redact_secrets(pk)
    assert "-----BEGIN RSA PRIVATE KEY-----" not in cleaned
    assert "[REDACTED_PRIVATE_KEY" in cleaned
    assert len(redactions) == 1

def test_sanitise_fields():
    raksha = get_raksha()
    fields = {
        "Notes": "Configure with sk-proj-1234567890abcdef1234567890abcdef",
        "Target": "Production",
        "Retries": 3
    }
    sanitized, redactions = raksha.sanitise_fields(fields)
    assert sanitized["Target"] == "Production"
    assert sanitized["Retries"] == 3
    assert "sk-proj" not in sanitized["Notes"]
    assert "[REDACTED_API_KEY:openai" in sanitized["Notes"]
    assert len(redactions) == 1
