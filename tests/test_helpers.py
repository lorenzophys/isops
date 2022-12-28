import pytest
from ruamel.yaml import YAML

from isops.utils import all_dict_values, find_by_key, load_all_yaml


def test_is_yaml_loaded_correctly(example_good_deploy_yaml):
    expected = {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {"name": "my-nginx", "labels": {"app": "nginx"}},
        "spec": {
            "replicas": 3,
            "selector": {"matchLabels": {"app": "nginx"}},
            "template": {
                "metadata": {"labels": {"app": "nginx"}},
                "spec": {
                    "containers": [
                        {
                            "name": "nginx",
                            "image": "nginx:1.14.2",
                            "ports": [{"containerPort": 80}],
                        }
                    ]
                },
            },
        },
    }
    assert isinstance(example_good_deploy_yaml, dict)
    assert example_good_deploy_yaml == expected


def test_bad_yaml_handled_correctly(example_bad_yaml):
    assert example_bad_yaml == {}


def test_bad_yaml_handled_correctly_load_all_yaml(tmp_path, example_bad_yaml_load_all):
    yaml = YAML(typ="safe")

    test_file = tmp_path / "root/test.yaml"
    test_file.parent.mkdir()

    yaml.dump(example_bad_yaml_load_all, test_file)

    yaml_file = load_all_yaml(test_file)
    assert yaml_file == [[]]


def test_find_by_key_one_target(simple_secret_yaml):
    target = "^data"
    expected = [{"data": {"username": "YWRtaW4=", "password": "MWYyZDFlMmU2N2Rm"}}]
    got = []
    for val in find_by_key(simple_secret_yaml, target):
        got.append(val)
    assert got == expected


def test_find_by_key_multiple_targets(example_good_deploy_yaml):
    target = "^app"
    expected = [{"app": "nginx"}] * 3
    got = []
    for val in find_by_key(example_good_deploy_yaml, target):
        got.append(val)
    assert got == expected


def test_find_by_key_regex(simple_secret_yaml):
    target = "^(data|metadata)$"
    expected = [
        {"data": {"username": "YWRtaW4=", "password": "MWYyZDFlMmU2N2Rm"}},
        {
            "metadata": {
                "name": "mysecret",
                "namespace": "default",
                "resourceVersion": "164619",
                "uid": "cfee02d6-c137-11e5-8d73-42010af00002",
            }
        },
    ]
    got = []
    for val in find_by_key(simple_secret_yaml, target):
        got.append(val)
    assert got == expected


@pytest.mark.parametrize(
    "key,value", [("image", "nginx:1.14.2"), ("containerPort", 80)]
)
def test_find_by_key_target_is_in_a_possibly_nested_list(
    example_good_deploy_yaml, key, value
):
    expected = [{key: value}]
    got = []
    for val in find_by_key(example_good_deploy_yaml, key):
        got.append(val)
    assert got == expected


def test_find_by_key_target_is_in_a_messy_nested_yaml(nested_yaml):
    key = "data"
    expected = [
        {
            "data": {
                "nested": {"username": "YWRtaW4=", "password": "MWYyZDFlMmU2N2Rm"},
                "another": [
                    {
                        "name": "nginx",
                        "image": "nginx:1.14.2",
                        "ports": [{"containerPort": 80}],
                    }
                ],
                "again": [
                    {
                        "name": "nginx_stable",
                        "image": "nginx:stable",
                        "ports": [{"containerPort": 443}],
                    }
                ],
                "onemore": [
                    "hello",
                    1,
                ],
            }
        }
    ]
    got = []
    for val in find_by_key(nested_yaml, key):
        got.append(val)
    assert got == expected


def test_find_by_key_but_no_match(nested_yaml):
    key = "idontexist"
    got = []
    for val in find_by_key(nested_yaml, key):
        got.append(val)
    assert got == []


def test_all_dict_values():
    input = {"data": {"username": "YWRtaW4=", "password": "MWYyZDFlMmU2N2Rm"}}
    expected = ["YWRtaW4=", "MWYyZDFlMmU2N2Rm"]
    got = []
    for _, val in all_dict_values(input):
        got.append(val)
    assert got == expected


def test_all_dict_values_nested_messy_yaml():
    input = {
        "data": {
            "nested": {"username": "YWRtaW4=", "password": "MWYyZDFlMmU2N2Rm"},
            "another": [
                {
                    "name": "nginx",
                    "image": "nginx:1.14.2",
                    "ports": [{"containerPort": 80}],
                }
            ],
            "again": [
                {
                    "name": "nginx_stable",
                    "image": "nginx:stable",
                    "ports": [{"containerPort": 443}],
                }
            ],
        }
    }
    expected = [
        "YWRtaW4=",
        "MWYyZDFlMmU2N2Rm",
        "nginx",
        "nginx:1.14.2",
        "80",
        "nginx_stable",
        "nginx:stable",
        "443",
    ]
    got = []
    for _, val in all_dict_values(input):
        got.append(val)
    assert got == expected
