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
