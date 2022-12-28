from isops.utils import verify_encryption_regex


def test_verify_encryption_regex(simple_enc_secret_yaml):
    secrets = [
        simple_enc_secret_yaml["data"]["username"],
        simple_enc_secret_yaml["data"]["password"],
        simple_enc_secret_yaml["sops"]["mac"],
    ]
    for secret in secrets:
        assert verify_encryption_regex(secret)

    not_secret = simple_enc_secret_yaml["sops"]["lastmodified"]
    assert verify_encryption_regex(not_secret) is None
