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

IOPS (Is OPerationsSecure) is a minimal command line utility to help you ensure that your secrets are encrypted correctly with sops before committing them.

## Usage example

Suppose you have a `.sops.yaml`:

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
bad-user@laptop:~$ iops ./example --config-regex .sops.yaml

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
good-user@laptop:~$ iops ./example --config-regex .sops.yaml

Found config file: example/.sops.yaml
example/secret.yaml::key [SAFE]
```

## Another example

You can have a more complicated scenario where there are multiple sops configuration files, multiple environments and lots of secrets. `iops` finds the config files by regex and then do the checks based on the `creation_rules` of each configuration. Then it tells you which secrets are safe to commit and what not.

Suppose you have this situation:

```text
examples
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
    ├── db-password-secret.yaml    <- Encrypted!
    ├── deployment.yaml
    └── service.yaml
```

Then if you run `iops` you get:

```console
user@laptop:~$ iops examples --config-regex "examples/.sops/(.*).yaml$"

Found config file: examples/.sops/sops-dev.yaml
Found config file: examples/.sops/sops-prod.yaml
examples/dev/db-password-secret.yaml::password [SAFE]
examples/dev/api-key-secret.yaml::key [SAFE]
examples/prod/db-password-secret.yaml::password [SAFE]
examples/prod/api-key-secret.yaml::key [UNSAFE]
```
