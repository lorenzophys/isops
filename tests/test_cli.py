import pytest
import yaml
from click.testing import CliRunner

from iops.cli import cli


@pytest.fixture(scope="function")
def simple_dir_struct(tmp_path, example_dotspos_yaml):
    """Functional programming shenanigans"""

    def _internal(yaml_to_test, config=example_dotspos_yaml):
        dotsops = tmp_path / "root/.sops.yaml"
        dotsops.parent.mkdir()
        dotsops.write_text(yaml.dump(config))
        secret = tmp_path / "root/secret.yaml"
        secret.write_text(yaml.dump(yaml_to_test))
        root = tmp_path / "root"
        return str(dotsops), str(secret), str(root), yaml_to_test

    return _internal


def test_cli_main_safe_file(simple_dir_struct, simple_enc_secret_yaml):
    # creation_rules:
    #     - path_regex: (.*)?secret.yaml$
    #         encrypted_regex: "^(data|stringData)$"
    #
    # and the secret has the "data" encrypted

    path_to_dotsops, path_to_yaml, root, _ = simple_dir_struct(simple_enc_secret_yaml)
    runner = CliRunner()
    result = runner.invoke(cli, [root, "--config-regex", ".sops.ya?ml"])

    expected_output = (
        f"Found config file: {path_to_dotsops}\n"
        f"{path_to_yaml}::password [SAFE]\n"
        f"{path_to_yaml}::username [SAFE]\n"
    )

    assert result.exit_code == 0
    assert result.output == expected_output


def test_cli_main_unsafe_file(simple_dir_struct, simple_secret_yaml):
    # creation_rules:
    #     - path_regex: \.enc\.yaml$
    #       encrypted_regex: "^(data|stringData)$"
    #
    # and the secret has the "data" NOT encrypted

    dotsops_path, yaml_path, root, _ = simple_dir_struct(simple_secret_yaml)
    runner = CliRunner()
    result = runner.invoke(cli, [root, "--config-regex", ".sops.ya?ml"])

    expected_output = (
        f"Found config file: {dotsops_path}\n"
        f"{yaml_path}::password [UNSAFE]\n"
        f"{yaml_path}::username [UNSAFE]\n"
    )

    assert result.exit_code == 1
    assert result.output == expected_output


def test_cli_main_dotsops_no_creation_rules(
    simple_dir_struct, simple_secret_yaml, example_dotspos_yaml_no_creation_rules
):
    # no 'creation_rules' key in a valid .sops.yaml

    dotsops_path, _, root, _ = simple_dir_struct(
        simple_secret_yaml, config=example_dotspos_yaml_no_creation_rules
    )
    runner = CliRunner()
    result = runner.invoke(cli, [root, "--config-regex", ".sops.ya?ml"])

    expected_output = "No valid config file found.\n"

    assert result.exit_code == 1
    assert result.output == expected_output


def test_cli_main_no_regex_path_no_enc_regex(
    simple_dir_struct, simple_enc_secret_yaml, example_dotspos_yaml_default_regex
):
    # the 'creation_rules' doesn't have neither 'path_regex' nor 'encrypted_regex',
    # so the default is applied

    dotsops_path, yaml_path, root, _ = simple_dir_struct(
        simple_enc_secret_yaml, config=example_dotspos_yaml_default_regex
    )
    runner = CliRunner()
    result = runner.invoke(cli, [root, "--config-regex", ".sops.ya?ml"])

    expected_output = (
        f"Found config file: {dotsops_path}\n"
        f"{dotsops_path}::pgp [UNSAFE]\n"
        f"{yaml_path}::apiVersion [UNSAFE]\n"
        f"{yaml_path}::kind [UNSAFE]\n"
        f"{yaml_path}::name [UNSAFE]\n"
        f"{yaml_path}::namespace [UNSAFE]\n"
        f"{yaml_path}::password [SAFE]\n"
        f"{yaml_path}::resourceVersion [UNSAFE]\n"
        f"{yaml_path}::type [UNSAFE]\n"
        f"{yaml_path}::uid [UNSAFE]\n"
        f"{yaml_path}::username [SAFE]\n"
    )

    assert result.exit_code == 1
    assert result.output == expected_output
