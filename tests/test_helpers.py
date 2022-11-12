import pytest
import yaml

from iops.utils import ensure_dotsops, find_by_key, get_all_values


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
    assert example_bad_yaml is None


@pytest.mark.parametrize("config", ["root/.sops.yaml", "root/.sops.yml"])
def test_ensure_dotsops_yaml_in_root_dir(example_dotspos_yaml, tmp_path, config):
    dotsops = tmp_path / config
    dotsops.parent.mkdir()
    dotsops.write_text(yaml.dump(example_dotspos_yaml))
    root = tmp_path / "root"
    assert ensure_dotsops(root) is not None


@pytest.mark.parametrize("config", [".sops/.sops.yaml", ".sops/.sops.yml"])
def test_ensure_dotsops_in_dotsops_dir(example_dotspos_yaml, tmp_path, config):
    root = tmp_path / "root"
    root.mkdir()
    dotsops = root / config
    dotsops.parent.mkdir()
    dotsops.write_text(yaml.dump(example_dotspos_yaml))
    root = tmp_path / "root"
    assert ensure_dotsops(root) is not None


def test_ensure_no_dotsops(tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    dotsops = root / "halo.yaml"
    dotsops.write_text("I'm not .sops.yaml")
    root = tmp_path / "root"
    assert ensure_dotsops(root) is None


def test_ensure_too_many_dotsops(example_dotspos_yaml, tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    dotsops_1 = root / ".sops/.sops.yaml"
    dotsops_1.parent.mkdir()
    dotsops_1.write_text(yaml.dump(example_dotspos_yaml))
    dotsops_2 = root / ".sops.yaml"
    dotsops_2.write_text(yaml.dump(example_dotspos_yaml))
    root = tmp_path / "root"
    assert ensure_dotsops(root) is None


def test_find_by_key_one_target(simple_secret_yaml):
    target = "data"
    expected = [{target: {"username": "YWRtaW4=", "password": "MWYyZDFlMmU2N2Rm"}}]
    got = []
    for val in find_by_key(simple_secret_yaml, target):
        got.append(val)
    assert got == expected


def test_find_by_key_multiple_targets(example_good_deploy_yaml):
    target = "app"
    expected = [{target: "nginx"}] * 3
    got = []
    for val in find_by_key(example_good_deploy_yaml, target):
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
            }
        }
    ]
    got = []
    for val in find_by_key(nested_yaml, key):
        got.append(val)
    assert got == expected


def test_get_all_values():
    input = {"data": {"username": "YWRtaW4=", "password": "MWYyZDFlMmU2N2Rm"}}
    expected = ["YWRtaW4=", "MWYyZDFlMmU2N2Rm"]
    got = []
    for val in get_all_values(input):
        got.append(val)
    assert got == expected


def test_get_all_values_nested_messy_yaml():
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
        80,
        "nginx_stable",
        "nginx:stable",
        443,
    ]
    got = []
    for val in get_all_values(input):
        got.append(val)
    assert got == expected
