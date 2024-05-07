import collections

import pytest
from click.testing import CliRunner
from ruamel.yaml import YAML

from isops.cli import cli


def assert_consistent_output(expected: str, actual: str) -> bool:
    # This is useful to avoid worrying about the ordering of the
    # printed output. It compares the content of the expected output
    # without taking into account the order in which it is printed.

    new_expected = expected.split("\n")
    new_actual = actual.split("\n")

    return collections.Counter(new_expected) == collections.Counter(new_actual)


@pytest.mark.parametrize("summary", [True, False])
def test_cli_main_safe_file(simple_dir_struct, simple_enc_secret_yaml, summary):
    # creation_rules:
    #     - path_regex: (.*)?secret.yaml$
    #         encrypted_regex: "^(data|stringData)$"
    #
    # and the secret has the "data" encrypted

    path_to_dotsops, path_to_yaml, root, _ = simple_dir_struct(simple_enc_secret_yaml)
    runner = CliRunner()
    if summary:
        result = runner.invoke(cli, [root, "--config-regex", ".sops.ya?ml", "--summary"])
        expected_output = (
            f"Found config file: {path_to_dotsops}\n"
            "---\n"
            f"{path_to_yaml}::password [SAFE]\n"
            f"{path_to_yaml}::username [SAFE]\n"
            "---\n"
            "Summary:\n"
            "2 safe 0 unsafe\n"
        )
    else:
        result = runner.invoke(cli, [root, "--config-regex", ".sops.ya?ml"])
        expected_output = (
            f"Found config file: {path_to_dotsops}\n"
            "---\n"
            f"{path_to_yaml}::password [SAFE]\n"
            f"{path_to_yaml}::username [SAFE]\n"
        )

    assert result.exit_code == 0
    assert assert_consistent_output(expected_output, result.output)


@pytest.mark.parametrize("summary", [True, False])
def test_cli_main_unsafe_file(simple_dir_struct, simple_secret_yaml, summary):
    # creation_rules:
    #     - path_regex: \.enc\.yaml$
    #       encrypted_regex: "^(data|stringData)$"
    #
    # and the secret has the "data" NOT encrypted

    dotsops_path, yaml_path, root, _ = simple_dir_struct(simple_secret_yaml)
    runner = CliRunner()

    if summary:
        result = runner.invoke(cli, [root, "--config-regex", ".sops.ya?ml", "--summary"])
        expected_output = (
            f"Found config file: {dotsops_path}\n"
            "---\n"
            f"{yaml_path}::username [UNSAFE]\n"
            f"{yaml_path}::password [UNSAFE]\n"
            "---\n"
            "Summary:\n"
            f"UNSAFE secret 'username' in '{yaml_path}'\n"
            f"UNSAFE secret 'password' in '{yaml_path}'\n"
            "0 safe 2 unsafe\n"
        )
    else:
        result = runner.invoke(cli, [root, "--config-regex", ".sops.ya?ml"])
        expected_output = (
            f"Found config file: {dotsops_path}\n"
            "---\n"
            f"{yaml_path}::username [UNSAFE]\n"
            f"{yaml_path}::password [UNSAFE]\n"
        )

    assert result.exit_code == 1
    assert assert_consistent_output(expected_output, result.output)


@pytest.mark.parametrize("summary", [True, False])
def test_cli_main_dotsops_no_creation_rules(
    simple_dir_struct,
    simple_secret_yaml,
    example_dotspos_yaml_no_creation_rules,
    summary,
):
    # no 'creation_rules' key in a valid .sops.yaml

    dotsops_path, _, root, _ = simple_dir_struct(
        simple_secret_yaml, config=example_dotspos_yaml_no_creation_rules
    )
    runner = CliRunner()

    if summary:
        result = runner.invoke(cli, [root, "--config-regex", ".sops.ya?ml", "--summary"])
    else:
        result = runner.invoke(cli, [root, "--config-regex", ".sops.ya?ml"])

    expected_output = f"WARNING: skipping '{dotsops_path}'\nNo valid config file found.\n"

    assert result.exit_code == 1
    assert assert_consistent_output(expected_output, result.output)


@pytest.mark.parametrize("summary", [True, False])
def test_cli_main_no_regex_path_no_enc_regex(
    simple_dir_struct,
    simple_enc_secret_yaml,
    example_dotspos_yaml_default_regex,
    summary,
):
    # the 'creation_rules' doesn't have neither 'path_regex' nor 'encrypted_regex',
    # so the default is applied

    dotsops_path, yaml_path, root, _ = simple_dir_struct(
        simple_enc_secret_yaml, config=example_dotspos_yaml_default_regex
    )
    runner = CliRunner()
    if summary:
        result = runner.invoke(cli, [root, "--config-regex", ".sops.ya?ml", "--summary"])
        expected_output = (
            f"Found config file: {dotsops_path}\n"
            "---\n"
            f"{dotsops_path}::pgp [UNSAFE]\n"
            f"{yaml_path}::uid [UNSAFE]\n"
            f"{yaml_path}::namespace [UNSAFE]\n"
            f"{yaml_path}::username [SAFE]\n"
            f"{yaml_path}::kind [UNSAFE]\n"
            f"{yaml_path}::name [UNSAFE]\n"
            f"{yaml_path}::apiVersion [UNSAFE]\n"
            f"{yaml_path}::password [SAFE]\n"
            f"{yaml_path}::type [UNSAFE]\n"
            f"{yaml_path}::resourceVersion [UNSAFE]\n"
            "---\n"
            "Summary:\n"
            f"UNSAFE secret 'pgp' in '{dotsops_path}'\n"
            f"UNSAFE secret 'uid' in '{yaml_path}'\n"
            f"UNSAFE secret 'namespace' in '{yaml_path}'\n"
            f"UNSAFE secret 'kind' in '{yaml_path}'\n"
            f"UNSAFE secret 'name' in '{yaml_path}'\n"
            f"UNSAFE secret 'apiVersion' in '{yaml_path}'\n"
            f"UNSAFE secret 'type' in '{yaml_path}'\n"
            f"UNSAFE secret 'resourceVersion' in '{yaml_path}'\n"
            "2 safe 8 unsafe\n"
        )
    else:
        result = runner.invoke(cli, [root, "--config-regex", ".sops.ya?ml"])
        expected_output = (
            f"Found config file: {dotsops_path}\n"
            "---\n"
            f"{dotsops_path}::pgp [UNSAFE]\n"
            f"{yaml_path}::uid [UNSAFE]\n"
            f"{yaml_path}::namespace [UNSAFE]\n"
            f"{yaml_path}::username [SAFE]\n"
            f"{yaml_path}::kind [UNSAFE]\n"
            f"{yaml_path}::name [UNSAFE]\n"
            f"{yaml_path}::apiVersion [UNSAFE]\n"
            f"{yaml_path}::password [SAFE]\n"
            f"{yaml_path}::type [UNSAFE]\n"
            f"{yaml_path}::resourceVersion [UNSAFE]\n"
        )

    assert result.exit_code == 1
    assert assert_consistent_output(expected_output, result.output)


def test_cli_invalid_regex_in_config_regex_option():
    # invalid regex in --config-regex
    runner = CliRunner()
    result = runner.invoke(cli, [".", "--config-regex", "["])

    assert result.exit_code == 2


@pytest.mark.parametrize("summary", [True, False])
def test_cli_main_dotsops_bad_path_regex(
    simple_dir_struct, simple_enc_secret_yaml, dot_sops_bad_path_regex, summary
):
    # invalid regex in 'path_regex'

    dotsops_path, yaml_path, root, _ = simple_dir_struct(
        simple_enc_secret_yaml, config=dot_sops_bad_path_regex
    )

    runner = CliRunner()
    if summary:
        result = runner.invoke(cli, [root, "--config-regex", ".sops.ya?ml", "--summary"])

    else:
        result = runner.invoke(cli, [root, "--config-regex", ".sops.ya?ml"])

    expected_output = (
        f"Found config file: {dotsops_path}\n" "---\n" "Invalid regex for 'path_regex': [\n"
    )

    assert result.exit_code == 1
    assert assert_consistent_output(expected_output, result.output)


@pytest.mark.parametrize("summary", [True, False])
def test_cli_main_dotsops_bad_encrypted_regex(
    simple_dir_struct, simple_enc_secret_yaml, dot_sops_bad_encrypted_regex, summary
):
    # invalid regex in 'path_regex'

    dotsops_path, yaml_path, root, _ = simple_dir_struct(
        simple_enc_secret_yaml, config=dot_sops_bad_encrypted_regex
    )

    runner = CliRunner()
    if summary:
        result = runner.invoke(cli, [root, "--config-regex", ".sops.ya?ml", "--summary"])
    else:
        result = runner.invoke(cli, [root, "--config-regex", ".sops.ya?ml"])

    expected_output = (
        f"Found config file: {dotsops_path}\n" "---\n" "Invalid regex for 'encrypted_regex': [\n"
    )

    assert result.exit_code == 1
    assert assert_consistent_output(expected_output, result.output)


@pytest.mark.parametrize("summary", [True, False])
def test_cli_two_config_files(
    tmp_path, dot_sops_one_rule, example_dotspos_yaml, simple_enc_secret_yaml, summary
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

    if summary:
        result = runner.invoke(cli, [str(root), "--config-regex", ".sops(.*)?.ya?ml", "--summary"])
        expected_output = (
            f"Found config file: {dotsops_2}\n"
            f"Found config file: {dotsops}\n"
            "---\n"
            f"{secret}::resourceVersion [UNSAFE]\n"
            f"{secret}::name [UNSAFE]\n"
            f"{secret}::namespace [UNSAFE]\n"
            f"{secret}::uid [UNSAFE]\n"
            f"{secret}::password [SAFE]\n"
            f"{secret}::username [SAFE]\n"
            "---\n"
            "Summary:\n"
            f"UNSAFE secret 'uid' in '{secret}'\n"
            f"UNSAFE secret 'namespace' in '{secret}'\n"
            f"UNSAFE secret 'name' in '{secret}'\n"
            f"UNSAFE secret 'resourceVersion' in '{secret}'\n"
            "2 safe 4 unsafe\n"
        )
    else:
        result = runner.invoke(cli, [str(root), "--config-regex", ".sops(.*)?.ya?ml"])
        expected_output = (
            f"Found config file: {dotsops_2}\n"
            f"Found config file: {dotsops}\n"
            "---\n"
            f"{secret}::resourceVersion [UNSAFE]\n"
            f"{secret}::name [UNSAFE]\n"
            f"{secret}::namespace [UNSAFE]\n"
            f"{secret}::uid [UNSAFE]\n"
            f"{secret}::password [SAFE]\n"
            f"{secret}::username [SAFE]\n"
        )

    assert result.exit_code == 1
    assert assert_consistent_output(expected_output, result.output)


@pytest.mark.parametrize("summary", [True, False])
def test_cli_secret_not_valid_yaml(tmp_path, example_dotspos_yaml, summary):
    # the secret is captured by the creation rules, but it's rubbish

    yaml = YAML(typ="safe")

    dotsops = tmp_path / "root/.sops.yaml"
    dotsops.parent.mkdir()
    yaml.dump(example_dotspos_yaml, dotsops)
    secret = tmp_path / "root/secret.yaml"
    secret.write_text("[")
    root = tmp_path / "root"

    runner = CliRunner()

    if summary:
        result = runner.invoke(cli, [str(root), "--config-regex", ".sops.ya?ml", "--summary"])
        expected_output = (
            f"Found config file: {dotsops}\n"
            "---\n"
            f"{secret} is not a valid YAML!\n"
            "---\n"
            "Summary:\n"
            f"The yaml '{secret}' is broken, checks incomplete!\n"
        )
        print(result.output)
    else:
        result = runner.invoke(cli, [str(root), "--config-regex", ".sops.ya?ml"])
        expected_output = (
            f"Found config file: {dotsops}\n" "---\n" f"{secret} is not a valid YAML!\n"
        )

    assert result.exit_code == 1
    assert assert_consistent_output(expected_output, result.output)


@pytest.mark.parametrize("summary", [True, False])
def test_cli_secret_is_a_block_of_yaml(tmp_path, example_dotspos_yaml, yaml_blocks, summary):
    # the secret is a block of yaml

    yaml = YAML(typ="safe")

    dotsops = tmp_path / "root/.sops.yaml"
    dotsops.parent.mkdir()
    yaml.dump(example_dotspos_yaml, dotsops)
    secret = tmp_path / "root/secret.yaml"
    yaml.dump_all(yaml_blocks, secret)
    root = tmp_path / "root"

    runner = CliRunner()

    if summary:
        result = runner.invoke(cli, [str(root), "--config-regex", ".sops.ya?ml", "--summary"])
        expected_output = (
            f"Found config file: {dotsops}\n"
            "---\n"
            f"{secret}::password [UNSAFE]\n"
            f"{secret}::username [UNSAFE]\n"
            f"{secret}::password [UNSAFE]\n"
            f"{secret}::username [UNSAFE]\n"
            "---\n"
            "Summary:\n"
            f"UNSAFE secret 'password' in '{secret}'\n"
            f"UNSAFE secret 'username' in '{secret}'\n"
            f"UNSAFE secret 'username' in '{secret}'\n"
            f"UNSAFE secret 'password' in '{secret}'\n"
            "0 safe 4 unsafe\n"
        )
    else:
        result = runner.invoke(cli, [str(root), "--config-regex", ".sops.ya?ml"])
        expected_output = (
            f"Found config file: {dotsops}\n"
            "---\n"
            f"{secret}::password [UNSAFE]\n"
            f"{secret}::username [UNSAFE]\n"
            f"{secret}::password [UNSAFE]\n"
            f"{secret}::username [UNSAFE]\n"
        )

    assert result.exit_code == 1
    assert assert_consistent_output(expected_output, result.output)
