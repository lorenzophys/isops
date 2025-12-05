import os
from pathlib import Path

import pytest
from ruamel.yaml import YAML

from isops.utils import (
    all_dict_values,
    detect_encoding,
    find_all_files_by_regex,
    find_by_key,
    load_all_yaml,
    load_all_yaml_with_encoding,
)

TESTS_PATH = os.path.dirname(os.path.realpath(__file__))
SAMPLES_PATH = os.path.join(TESTS_PATH, "samples")


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


@pytest.mark.parametrize("key,value", [("image", "nginx:1.14.2"), ("containerPort", 80)])
def test_find_by_key_target_is_in_a_possibly_nested_list(example_good_deploy_yaml, key, value):
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


def test_utf16_yaml_loaded_correctly(simple_secret_utf16_yaml):
    """Test that UTF-16 encoded YAML files are loaded correctly"""
    expected = {
        "apiVersion": "v1",
        "data": {"username": "YWRtaW4=", "password": "MWYyZDFlMmU2N2Rm"},
        "kind": "Secret",
        "metadata": {"name": "mysecret-utf16", "namespace": "default"},
        "type": "Opaque",
    }
    assert isinstance(simple_secret_utf16_yaml, dict)
    assert simple_secret_utf16_yaml == expected


def test_utf16_encoding_detection():
    """Test that UTF-16 encoding is correctly detected"""
    path = Path(os.path.join(SAMPLES_PATH, "simple_secret_utf16.yaml"))
    encoding = detect_encoding(path)
    assert encoding is not None
    assert encoding.startswith("utf-16")


def test_load_all_yaml_with_encoding_utf16():
    """Test that load_all_yaml_with_encoding returns correct data and encoding for UTF-16 files"""
    path = Path(os.path.join(SAMPLES_PATH, "simple_secret_utf16.yaml"))
    data, encoding = load_all_yaml_with_encoding(path)

    assert len(data) == 1
    assert encoding is not None
    assert encoding.startswith("utf-16")
    assert data[0]["kind"] == "Secret"
    assert data[0]["metadata"]["name"] == "mysecret-utf16"


def test_load_all_yaml_with_encoding_utf8():
    """Test that load_all_yaml_with_encoding returns correct data and encoding for UTF-8 files"""
    path = Path(os.path.join(SAMPLES_PATH, "simple_secret.yaml"))
    data, encoding = load_all_yaml_with_encoding(path)

    assert len(data) == 1
    assert encoding == "utf-8"
    assert data[0]["kind"] == "Secret"


def test_utf16_encrypted_yaml_loaded_correctly(simple_secret_utf16_enc_yaml):
    """Test that UTF-16 encoded encrypted YAML files are loaded correctly"""
    assert isinstance(simple_secret_utf16_enc_yaml, dict)
    assert simple_secret_utf16_enc_yaml["kind"] == "Secret"
    assert simple_secret_utf16_enc_yaml["metadata"]["name"] == "mysecret-utf16-enc"
    # Check that encrypted values start with ENC[
    assert simple_secret_utf16_enc_yaml["data"]["username"].startswith("ENC[")
    assert simple_secret_utf16_enc_yaml["data"]["password"].startswith("ENC[")


def test_find_all_files_respects_gitignore(tmp_path):
    """Test that find_all_files_by_regex respects .gitignore patterns"""
    # Create test directory structure
    (tmp_path / "included").mkdir()
    (tmp_path / "ignored_dir").mkdir()
    (tmp_path / "nested" / "ignored_nested").mkdir(parents=True)

    # Create test files
    (tmp_path / "file1.yaml").write_text("test: 1")
    (tmp_path / "file2.yaml").write_text("test: 2")
    (tmp_path / "included" / "file3.yaml").write_text("test: 3")
    (tmp_path / "ignored_dir" / "file4.yaml").write_text("test: 4")
    (tmp_path / "ignored_file.yaml").write_text("test: ignored")
    (tmp_path / "nested" / "file5.yaml").write_text("test: 5")
    (tmp_path / "nested" / "ignored_nested" / "file6.yaml").write_text("test: 6")

    # Create .gitignore
    gitignore_content = """# Ignore specific directory
ignored_dir/
# Ignore specific file
ignored_file.yaml
# Ignore nested directory
nested/ignored_nested/
"""
    (tmp_path / ".gitignore").write_text(gitignore_content)

    # Find all YAML files
    found_files = list(find_all_files_by_regex(r"\.yaml$", tmp_path))
    found_names = {f.name for f in found_files}

    # Should find files that are not ignored
    assert "file1.yaml" in found_names
    assert "file2.yaml" in found_names
    assert "file3.yaml" in found_names
    assert "file5.yaml" in found_names
    assert ".gitignore" not in found_names

    # Should NOT find ignored files
    assert "ignored_file.yaml" not in found_names
    assert "file4.yaml" not in found_names  # in ignored_dir
    assert "file6.yaml" not in found_names  # in ignored_nested


def test_find_all_files_without_gitignore(tmp_path):
    """Test that find_all_files_by_regex works without .gitignore"""
    # Create test files
    (tmp_path / "file1.yaml").write_text("test: 1")
    (tmp_path / "file2.yaml").write_text("test: 2")
    (tmp_path / "subdir").mkdir()
    (tmp_path / "subdir" / "file3.yaml").write_text("test: 3")

    # Find all YAML files (no .gitignore exists)
    found_files = list(find_all_files_by_regex(r"\.yaml$", tmp_path))
    found_names = {f.name for f in found_files}

    # Should find all files
    assert len(found_names) == 3
    assert "file1.yaml" in found_names
    assert "file2.yaml" in found_names
    assert "file3.yaml" in found_names
