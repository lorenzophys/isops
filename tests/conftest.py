import os
from pathlib import Path

import pytest
from ruamel.yaml import YAML

from iops.utils import load_yaml

TESTS_PATH = os.path.dirname(os.path.realpath(__file__))
SAMPLES_PATH = os.path.join(TESTS_PATH, "samples")


@pytest.fixture(scope="function")
def simple_dir_struct(tmp_path, example_dotspos_yaml):
    """Nobody forbids me to make a fixture that returns a function"""

    def _internal(yaml_to_test, config=example_dotspos_yaml):
        yaml = YAML(typ="safe")

        dotsops = tmp_path / "root/.sops.yaml"
        dotsops.parent.mkdir()
        yaml.dump(config, dotsops)
        secret = tmp_path / "root/secret.yaml"
        yaml.dump(yaml_to_test, secret)
        root = tmp_path / "root"
        return str(dotsops), str(secret), str(root), yaml_to_test

    return _internal


@pytest.fixture(scope="function")
def example_good_deploy_yaml():
    path = Path(os.path.join(SAMPLES_PATH, "good_deploy_yaml.yaml"))
    return load_yaml(path)


@pytest.fixture(scope="function")
def example_bad_yaml():
    path = Path(os.path.join(SAMPLES_PATH, "bad_yaml.yaml"))
    return load_yaml(path)


@pytest.fixture(scope="function")
def example_dotspos_yaml():
    path = Path(os.path.join(SAMPLES_PATH, ".sops.yaml"))
    return load_yaml(path)


@pytest.fixture(scope="function")
def example_dotspos_yaml_no_creation_rules():
    path = Path(os.path.join(SAMPLES_PATH, ".sops_no_creation_rules.yaml"))
    return load_yaml(path)


@pytest.fixture(scope="function")
def example_dotspos_yaml_default_regex():
    path = Path(os.path.join(SAMPLES_PATH, ".sops_default_regex.yaml"))
    return load_yaml(path)


@pytest.fixture(scope="function")
def simple_secret_yaml():
    path = Path(os.path.join(SAMPLES_PATH, "simple_secret.yaml"))
    return load_yaml(path)


@pytest.fixture(scope="function")
def simple_enc_secret_yaml():
    path = Path(os.path.join(SAMPLES_PATH, "simple_secret.enc.yaml"))
    return load_yaml(path)


@pytest.fixture(scope="function")
def nested_yaml():
    path = Path(os.path.join(SAMPLES_PATH, "nested_sample.yaml"))
    return load_yaml(path)


@pytest.fixture(scope="function")
def dot_sops_bad_path_regex():
    path = Path(os.path.join(SAMPLES_PATH, ".sops_bad_path_regex.yaml"))
    return load_yaml(path)


@pytest.fixture(scope="function")
def dot_sops_bad_encrypted_regex():
    path = Path(os.path.join(SAMPLES_PATH, ".sops_bad_encrypted_regex.yaml"))
    return load_yaml(path)


@pytest.fixture(scope="function")
def dot_sops_one_rule():
    path = Path(os.path.join(SAMPLES_PATH, ".sops_one_rule.yaml"))
    return load_yaml(path)
