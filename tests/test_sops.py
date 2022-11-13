from pathlib import Path

import pytest
import yaml

from iops.utils import ensure_dotsops, verify_encryption_regex


@pytest.mark.parametrize("config", ["root/.sops.yaml", "root/.sops.yml"])
def test_ensure_dotsops_yaml_in_root_dir(example_dotspos_yaml, tmp_path, config):
    dotsops = tmp_path / config
    dotsops.parent.mkdir()
    dotsops.write_text(yaml.dump(example_dotspos_yaml))
    root = tmp_path / "root"
    dotsops_path, content = ensure_dotsops(root)
    assert dotsops_path == dotsops
    assert content != {}


@pytest.mark.parametrize("config", [".sops/.sops.yaml", ".sops/.sops.yml"])
def test_ensure_dotsops_in_dotsops_dir(example_dotspos_yaml, tmp_path, config):
    root = tmp_path / "root"
    root.mkdir()
    dotsops = root / config
    dotsops.parent.mkdir()
    dotsops.write_text(yaml.dump(example_dotspos_yaml))
    root = tmp_path / "root"
    dotsops_path, content = ensure_dotsops(root)
    assert dotsops_path == dotsops
    assert content != {}


def test_ensure_no_dotsops(tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    dotsops = root / "halo.yaml"
    dotsops.write_text("I'm not .sops.yaml")
    root = tmp_path / "root"
    dotsops_path, content = ensure_dotsops(root)
    assert dotsops_path == Path("NonePath")
    assert content == {}


def test_ensure_too_many_dotsops(example_dotspos_yaml, tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    dotsops_1 = root / ".sops/.sops.yaml"
    dotsops_1.parent.mkdir()
    dotsops_1.write_text(yaml.dump(example_dotspos_yaml))
    dotsops_2 = root / ".sops.yaml"
    dotsops_2.write_text(yaml.dump(example_dotspos_yaml))
    root = tmp_path / "root"
    dotsops_path, content = ensure_dotsops(root)
    assert dotsops_path == Path("NonePath")
    assert content == {}


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
