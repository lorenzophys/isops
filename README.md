# IsOPS: **Is** **OP**erations **S**ecure

![release](https://img.shields.io/github/v/release/lorenzophys/isops)
[![codecov](https://codecov.io/gh/lorenzophys/isops/branch/main/graph/badge.svg?token=7RQ5P3X22D)](https://codecov.io/gh/lorenzophys/isops)
![GitHub Workflow Status (with branch)](https://img.shields.io/github/actions/workflow/status/lorenzophys/isops/test-workflow.yml?branch=main&label=tests)
![pver](https://img.shields.io/pypi/pyversions/isops)
![MIT](https://img.shields.io/github/license/lorenzophys/isops)

```ascii
__/\\\\\\\\\\\____________________/\\\\\_______/\\\\\\\\\\\\\_______/\\\\\\\\\\\___        
 _\/////\\\///___________________/\\\///\\\____\/\\\/////////\\\___/\\\/////////\\\_       
  _____\/\\\____________________/\\\/__\///\\\__\/\\\_______\/\\\__\//\\\______\///__      
   _____\/\\\______/\\\\\\\\\\__/\\\______\//\\\_\/\\\\\\\\\\\\\/____\////\\\_________     
    _____\/\\\_____\/\\\//////__\/\\\_______\/\\\_\/\\\/////////_________\////\\\______    
     _____\/\\\_____\/\\\\\\\\\\_\//\\\______/\\\__\/\\\_____________________\////\\\___   
      _____\/\\\_____\////////\\\__\///\\\__/\\\____\/\\\______________/\\\______\//\\\__  
       __/\\\\\\\\\\\__/\\\\\\\\\\____\///\\\\\/_____\/\\\_____________\///\\\\\\\\\\\/___ 
        _\///////////__\//////////_______\/////_______\///________________\///////////_____

```

IsOPS (**Is** **OP**erations **S**ecure) is a minimal command line utility that helps you ensure that your secrets are encrypted correctly with [sops](https://github.com/mozilla/sops) before committing them. `isops` will read your configuration files, will scan all your secrets and alerts you if it finds any key that should be encrypted but it's not.

## Installation

You can install `isops` via `pip`:

```console
user@laptop:~$ pip install isops
```

The CLI is minimal:

```console
user@laptop:~$ isops
Usage: isops [OPTIONS] PATH

  Utility to ensure all SOPS secrets are encrypterd.

Options:
  -s, --summary            Print a summary at the end of the checks.
  -h, --help               Show this message and exit.
  -v, --version            Show the version and exit.
  -r, --config-regex TEXT  The regex that matches all the config files to use.
                           [required]
```

You must provide a directory to scan and a regex that matches all the sops configuration files.

## How it works?

`isops` is called with a directory and a regex. Then:

1. It finds the config files using the provided regex.
2. For each rule in `creation_rules` it finds the files according to the `path_regex`.
3. For each file found, it scans all the keys, no matter how nested the yaml is, in search for those keys that match the `encrypted_regex`.
4. For each matched key, it checks if the associated value matches the sops regex `"^ENC\[AES256_GCM,data:(.+),iv:(.+),tag:(.+),type:(.+)\]"`.

If the config file doesn't provide a `path_regex` or a `encrypted_regex`, the default values are, respectively, `".ya?ml$"` and `""`.

## Usage example

Suppose you have this situation:

```text
example
├── .sops.yaml
└── secret.yaml
```

A `.sops.yaml`:

```yaml
creation_rules:
  - path_regex: (.*)?secret.yaml$
    encrypted_regex: "^(data|stringData)$"
    pgp: "FBC7B9E2A4F9289AC0C1D4843D16CEE4A27381B4"
```

and a `secret.yaml`:

```yaml
apiVersion: v1
data:
  key: aGhkZDg4OGRoODRmaDQ4ZmJlbnNta21rbHdtc2k4
kind: Secret
metadata:
  name: api-key
type: Opaque
```

If you run `isops` you get a warning because your secret is not encrypted:

```console
user@laptop:~$ isops ./example --config-regex .sops.yaml
Found config file: example/.sops.yaml
---
example/secret.yaml::key [UNSAFE]
user@laptop:~$ echo $?
1
```

If the same secret is encrypted with sops:

```yaml
apiVersion: v1
data:
    key: ENC[AES256_GCM,data:iCBh27Ort/dNVhP9D4y/AqI5d78U+2EHtHPX9u0/s9ANhA2VeqKSOQ==,iv:HkQVUgB6nvN3TU355K/PTU2NroahHAdoJhzJdgZFMwo=,tag:ayNppVmYJ/MLGrW9RtjV1A==,type:str]
kind: Secret
metadata:
    name: api-key
type: Opaque
sops:
    etc...

```

then `isops` will give you the green light:

```console
user@laptop:~$ isops ./example --config-regex .sops.yaml
Found config file: example/.sops.yaml
---
example/secret.yaml::key [SAFE]
user@laptop:~$ echo $?
0
```

## Another example

You can have a more complicated scenario where there are multiple sops configuration files, multiple environments and lots of secrets.

Suppose you have this situation:

```text
example
├── .sops
│   ├── sops-dev.yaml
│   └── sops-prod.yaml
├── dev
│   ├── api-key-secret.yaml        <- Encrypted
│   ├── db-password-secret.yaml    <- Encrypted
│   ├── deployment.yaml
│   └── service.yaml
└── prod
    ├── api-key-secret.yaml        <- Not encrypted!
    ├── db-password-secret.yaml    <- Encrypted
    ├── deployment.yaml
    └── service.yaml
```

Then if you run `isops` you get:

```console
user@laptop:~$ isops example --config-regex "example/.sops/(.*).yaml$"
Found config file: example/.sops/sops-dev.yaml
Found config file: example/.sops/sops-prod.yaml
---
example/dev/db-password-secret.yaml::password [SAFE]
example/dev/api-key-secret.yaml::key [SAFE]
example/prod/db-password-secret.yaml::password [SAFE]
example/prod/api-key-secret.yaml::key [UNSAFE]
```

Sometimes the list of secret is very long: you can enable a small summary at the end with the `--summary` option:

```console
user@laptop:~$ isops example --config-regex "example/.sops/(.*).yaml$" --summary
Found config file: example/.sops/sops-dev.yaml
Found config file: example/.sops/sops-prod.yaml
---
example/dev/db-password-secret.yaml::password [SAFE]
example/dev/api-key-secret.yaml::key [SAFE]
example/prod/db-password-secret.yaml::password [SAFE]
example/prod/api-key-secret.yaml::key [UNSAFE]
---
Summary:
UNSAFE secret 'key' in 'example/prod/api-key-secret.yaml'
3 safe 1 unsafe
```

The previous example can be found in the `example` directory. The sample application was generated by [ChatGPT](https://chat.openai.com/chat) with the prompt: "Please, generate an example Kubernetes application with two secrets".

## `pre-commit` hook

`isops` can be also used as a [pre-commit](https://pre-commit.com) hook. For example:

```yaml
repos:
  - repo: https://github.com/lorenzophys/isops
    rev: v0.2.0
    hooks:
      - id: isops
        args:
          - --config-regex=.sops/(.*).ya?ml$
          - --summary
```

## License

This project is licensed under the **MIT License** - see the *LICENSE* file for details.
