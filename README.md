# Cirun Python Client and CLI

[![PyPI - Version](https://img.shields.io/pypi/v/cirun.svg)](https://pypi.org/project/cirun)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/cirun.svg)](https://pypi.org/project/cirun)

-----

**Table of Contents**

- [Installation](#installation)
- [Usage](#license)
- [License](#license)

## Installation

```console
pip install cirun
```

or via `conda-forge`

```console
conda install -c conda-forge cirun
```

## Usage

**cirun-py** can be used as a CLI as well as a Python client programmatically.

- Create an API key from the Cirun Dashboard https://cirun.io/admin/api
- Set that API Key as an environment variable named `CIRUN_API_KEY`

```console
export CIRUN_API_KEY=<your-api-key>
```

### CLI

- List active repositories for Cirun

```bash
$ cirun repo list
──────────────────────────────────────────────────────────────────────────────────────────────────────────
{
  "repos": [
    {
      "repository": "aktech/cirun-openstack-example",
      "active": true,
      "private": false
    },
    {
      "repository": "aktechlabs/cirun-demo",
      "active": true,
      "private": true
    }
  ]
}
──────────────────────────────────────────────────────────────────────────────────────────────────────────
```

- Active (add) a repository

```bash
$ cirun repo add aktech/sympy
──────────────────────────────────────────────────────────────────────────────────────────────────────────
{
  "name": "aktech/sympy",
  "active": true
}
──────────────────────────────────────────────────────────────────────────────────────────────────────────
```

- Deactivate (remove) a repository

```bash
$ cirun repo remove aktech/sympy
──────────────────────────────────────────────────────────────────────────────────────────────────────────
{
  "name": "aktech/sympy",
  "active": false
}
──────────────────────────────────────────────────────────────────────────────────────────────────────────
```

- Connect cloud provider with Cirun

```bash
cirun cloud connect aws --access-key AKIXXXXXXXXX --secret-key KFCF3yi+df0n12345678AMASDFGHJ

cirun cloud connect azure \
  --subscription-id 31184337-0346-4782-ae59-eb185fd0cfa1 \
  --tenant-id a66e466d-698b-4a91-b9e3-949f9cc04f11 \
  --client-id 340d01fc-ba24-43ee-844e-d364899d29e7 \
  --client-secret KFCF3yi+df0cirunIsAwesomeIsntIt?n1DFGHJ

cirun cloud connect gcp --key-file /path/to/service-account-key.json
```

### Client

```python
from cirun import Cirun
# Create cirun client object
# Pass the token or set `CIRUN_API_KEY` environment variable
c = Cirun(token='cirun-4cabcdbf-275c-4500-890d-712340663ddc')

# List repositories
c.get_repos()

# Active (add) a repository
c.set_repo('aktech/sympy', active=True)

# Deactivate (remove) a repository
c.set_repo('aktech/sympy', active=False)
```

## License

`cirun` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
