# IOPS

```ascii
__/\\\\\\\\\\\________/\\\\\________/\\\\\\\\\\\\\________/\\\\\\\\\\\___        
 _\/////\\\///_______/\\\///\\\_____\/\\\/////////\\\____/\\\/////////\\\_       
  _____\/\\\________/\\\/__\///\\\___\/\\\_______\/\\\___\//\\\______\///__      
   _____\/\\\_______/\\\______\//\\\__\/\\\\\\\\\\\\\/_____\////\\\_________     
    _____\/\\\______\/\\\_______\/\\\__\/\\\/////////__________\////\\\______    
     _____\/\\\______\//\\\______/\\\___\/\\\______________________\////\\\___   
      _____\/\\\_______\///\\\__/\\\_____\/\\\_______________/\\\______\//\\\__  
       __/\\\\\\\\\\\_____\///\\\\\/______\/\\\______________\///\\\\\\\\\\\/___ 
        _\///////////________\/////________\///_________________\///////////_____
```

IOPS (**I**s **OP**erations **S**ecure) is a minimal command line utility to help you ensure that your secrets are encrypted correctly with [sops](https://github.com/mozilla/sops) before committing them.

`iops` can read the sops config file, scan the relevant yaml files and tell you precisely the status of each key in each file.

## CLI

```console
user@laptop:~$ iops
Usage: iops [OPTIONS] PATH

  Top level command.

Options:
  -h, --help           Show this message and exit.
  --version            Show the version and exit.
  --config-regex TEXT  The regex that matches all the config files to use.
                       [required]
```

You must provide a directory to scan and a regex that captures all yous sops configuration files.

## How does it work?

`iops` is called with a directory and a regex. Then:

1. It finds the config files by the provided regex.
2. For each `creation_rules` it finds the files according to the `path_regex`.
3. For each file found, `iops` scans all the keys, no matter how nested the yaml is, in search for those key that match the `encrypted_regex`.
4. For each matched key, it checks if the associated value matches the sops regex `"^ENC\[AES256_GCM,data:(.+),iv:(.+),tag:(.+),type:(.+)\]"`.

If the config file doesn't provide a `path_regex` or a `encrypted_regex`, the default values are, respectively, `"\.ya?ml$"` and `""`.

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

and a secret:

```yaml
apiVersion: v1
data:
  key: aGhkZDg4OGRoODRmaDQ4ZmJlbnNta21rbHdtc2k4
kind: Secret
metadata:
  name: api-key
type: Opaque
```

If you run `iops` you get a warning because your secret is not encrypted:

```console
user@laptop:~$ iops ./example --config-regex .sops.yaml
Found config file: example/.sops.yaml
example/secret.yaml::key [UNSAFE]
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

then `iops` will give you the green light:

```console
user@laptop:~$ iops ./example --config-regex .sops.yaml
Found config file: example/.sops.yaml
example/secret.yaml::key [SAFE]
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

Then if you run `iops` you get:

```console
user@laptop:~$ iops example --config-regex "example/.sops/(.*).yaml$"
Found config file: example/.sops/sops-dev.yaml
Found config file: example/.sops/sops-prod.yaml
example/dev/db-password-secret.yaml::password [SAFE]
example/dev/api-key-secret.yaml::key [SAFE]
example/prod/db-password-secret.yaml::password [SAFE]
example/prod/api-key-secret.yaml::key [UNSAFE]
```

The previous example can be found in the `example` directory. The sample application was generated by [ChatGPT](https://chat.openai.com/chat) with the prompt: "Please, generate an example Kubernetes application with two secrets".
