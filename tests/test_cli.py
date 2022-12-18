from click.testing import CliRunner
from ruamel.yaml import YAML

from iops.cli import cli


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

    expected_output = (
        f"WARNING: skipping '{dotsops_path}'\nNo valid config file found.\n"
    )

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


def test_cli_invalid_regex_in_config_regex_option():
    # invalid regex in --config-regex
    runner = CliRunner()
    result = runner.invoke(cli, [".", "--config-regex", "["])

    assert result.exit_code == 2


def test_cli_main_dotsops_bad_path_regex(
    simple_dir_struct, simple_enc_secret_yaml, dot_sops_bad_path_regex
):
    # invalid regex in 'path_regex'

    dotsops_path, yaml_path, root, _ = simple_dir_struct(
        simple_enc_secret_yaml, config=dot_sops_bad_path_regex
    )

    runner = CliRunner()
    result = runner.invoke(cli, [root, "--config-regex", ".sops.ya?ml"])

    expected_output = (
        f"Found config file: {dotsops_path}\n" f"Invalid regex for 'path_regex': [\n"
    )

    assert result.exit_code == 1
    assert result.output == expected_output


def test_cli_main_dotsops_bad_encrypted_regex(
    simple_dir_struct, simple_enc_secret_yaml, dot_sops_bad_encrypted_regex
):
    # invalid regex in 'path_regex'

    dotsops_path, yaml_path, root, _ = simple_dir_struct(
        simple_enc_secret_yaml, config=dot_sops_bad_encrypted_regex
    )

    runner = CliRunner()
    result = runner.invoke(cli, [root, "--config-regex", ".sops.ya?ml"])

    expected_output = (
        f"Found config file: {dotsops_path}\n"
        f"Invalid regex for 'encrypted_regex': [\n"
    )

    assert result.exit_code == 1
    assert result.output == expected_output


def test_cli_two_config_files(
    tmp_path, dot_sops_one_rule, example_dotspos_yaml, simple_enc_secret_yaml
):
    # two config files should merge the creation_rules

    yaml = YAML(typ="safe")

    dotsops = tmp_path / "root/.sops.yaml"
    dotsops.parent.mkdir()
    dotsops_2 = tmp_path / "root/.sops_2.yaml"
    yaml.dump(example_dotspos_yaml, dotsops)
    yaml.dump(dot_sops_one_rule, dotsops_2)
    secret = tmp_path / "root/secret.yaml"
    yaml.dump(simple_enc_secret_yaml, secret)
    root = tmp_path / "root"

    runner = CliRunner()
    result = runner.invoke(cli, [str(root), "--config-regex", ".sops(.*)?.ya?ml"])

    expected_output = (
        f"Found config file: {dotsops_2}\n"
        f"Found config file: {dotsops}\n"
        f"{secret}::name [UNSAFE]\n"
        f"{secret}::namespace [UNSAFE]\n"
        f"{secret}::resourceVersion [UNSAFE]\n"
        f"{secret}::uid [UNSAFE]\n"
        f"{secret}::password [SAFE]\n"
        f"{secret}::username [SAFE]\n"
    )

    assert result.exit_code == 1
    assert result.output == expected_output


def test_cli_secret_not_valid_yaml(tmp_path, example_dotspos_yaml, example_bad_yaml):
    # the secret is captured by the creation rules, but it's rubbish

    yaml = YAML(typ="safe")

    dotsops = tmp_path / "root/.sops.yaml"
    dotsops.parent.mkdir()
    yaml.dump(example_dotspos_yaml, dotsops)
    secret = tmp_path / "root/secret.yaml"
    yaml.dump(example_bad_yaml, secret)
    root = tmp_path / "root"

    runner = CliRunner()
    result = runner.invoke(cli, [str(root), "--config-regex", ".sops.ya?ml"])

    expected_output = (
        f"Found config file: {dotsops}\n" f"{secret} is not a valid YAML!\n"
    )

    assert result.exit_code == 1
    assert result.output == expected_output
