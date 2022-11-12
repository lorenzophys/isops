import os

import pytest

from iops.utils import load_yaml

TESTS_PATH = os.path.dirname(os.path.realpath(__file__))
SAMPLES_PATH = os.path.join(TESTS_PATH, "samples")


@pytest.fixture(scope="module")
def example_good_deploy_yaml():
    path = os.path.join(SAMPLES_PATH, "good_deploy_yaml.yaml")
    return load_yaml(path)


@pytest.fixture(scope="module")
def example_bad_yaml():
    path = os.path.join(SAMPLES_PATH, "bad_yaml.yaml")
    return load_yaml(path)


@pytest.fixture(scope="module")
def example_dotspos_yaml():
    path = os.path.join(SAMPLES_PATH, ".sops.yaml")
    return load_yaml(path)


@pytest.fixture(scope="module")
def simple_secret_yaml():
    path = os.path.join(SAMPLES_PATH, "simple_secret.yaml")
    return load_yaml(path)


@pytest.fixture(scope="module")
def simple_enc_secret_yaml():
    path = os.path.join(SAMPLES_PATH, "simple_secret.enc.yaml")
    return load_yaml(path)


@pytest.fixture(scope="module")
def nested_yaml():
    path = os.path.join(SAMPLES_PATH, "nested_sample.yaml")
    return load_yaml(path)


# @pytest.fixture(scope="function")
# def directory_tree(tmp_path):
#     # Make root dir
#     root = tmp_path / "root"
#     root.mkdir()
#     # Make .sops/.sops.yaml
#     dotsops = root / ".sops"
#     dotsops.mkdir()
#     dotsops_yaml = dotsops / ".sops.yaml"
#     dotsops_yaml.write_text("CONTENT")
#     # Make manifests
#     manifests = root / "manifests"
#     manifests.mkdir()
#     # Test deploy
#     deploy = manifests / "deployment.yaml"
#     # Make secrets
#     secrets = manifests / "secrets"
#     secrets.mkdir()

#     list_dirs = os.walk(root)
#     for root, dirs, files in list_dirs:
#         for d in dirs:
#             splitted = str(os.path.join(root, d)).split("/")[10:]
#             print("/".join(splitted))
#         for f in files:
#             splitted = str(os.path.join(root, f)).split("/")[10:]
#             print("/".join(splitted))
