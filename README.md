# cirun-py

<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" alt="Cirun logo" height="150" srcset="https://raw.githubusercontent.com/AktechLabs/cirun-docs/refs/heads/main/static/img/cirun-logo-dark.svg">
    <source media="(prefers-color-scheme: light)" alt="Cirun logo" height="150" srcset="https://raw.githubusercontent.com/AktechLabs/cirun-docs/refs/heads/main/static/img/cirun-logo-light.svg">
    <img alt="Cirun logo" height="150" src="https://raw.githubusercontent.com/AktechLabs/cirun-docs/refs/heads/main/static/img/cirun-logo-light.svg">
  </picture>

  <h3>Python Client and CLI for the Cirun Platform</h3>

  [![PyPI - Version](https://img.shields.io/pypi/v/cirun.svg?style=for-the-badge&logo=pypi&logoColor=white)](https://pypi.org/project/cirun)
  [![PyPI - Python Version](https://img.shields.io/pypi/pyversions/cirun.svg?style=for-the-badge&logo=python&logoColor=white)](https://pypi.org/project/cirun)
  [![Conda Downloads](https://img.shields.io/conda/dn/conda-forge/cirun.svg?style=for-the-badge&logo=anaconda&logoColor=white)](https://anaconda.org/conda-forge/cirun)
  [![Conda Recipe](https://img.shields.io/badge/recipe-cirun-green.svg?style=for-the-badge&logo=conda-forge&logoColor=white)](https://anaconda.org/conda-forge/cirun)
  [![License](https://img.shields.io/badge/license-MIT-%23yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
  [![Documentation](https://img.shields.io/badge/docs-cirun-%230075A8.svg?style=for-the-badge)](https://docs.cirun.io)
</div>

## 🚀 Overview

**cirun-py** is a Python client and command-line interface for the [Cirun platform](https://cirun.io), enabling seamless management of your CI/CD infrastructure. Whether you're managing repositories, or connecting cloud providers, cirun-py makes it simple with both a programmatic API and intuitive CLI.

## ✨ Features

- **Dual Interface**: Use as both a Python client library and CLI tool
- **Repository Management**: Easily activate, deactivate, and list repositories
- **Cloud Provider Integration**: Connect AWS, Azure, GCP, and other cloud providers
- **Elegant API**: Clean, Pythonic interface for all Cirun operations
- **Rich Output Formatting**: Beautiful CLI output for better readability

## 📦 Installation

### Using pip (Recommended)

```bash
pip install cirun
```

### Using conda

```bash
conda install -c conda-forge cirun
```

### From Source

```bash
git clone https://github.com/cirun-io/cirun-py
cd cirun-py
pip install -e .
```

## 🏃‍♂️ Quick Start

1. **Get your API key** from the [Cirun dashboard](https://cirun.io/admin/api)
2. **Set your API key as an environment variable**:

```bash
export CIRUN_API_KEY=<your-api-key>
```

3. **Start using cirun-py!**

## 🧰 Usage

### CLI Examples

#### Repository Management

```bash
# List active repositories
cirun repo list

# Activate a repository
cirun repo add username/repo-name

# Deactivate a repository
cirun repo remove username/repo-name
```

#### Cloud Provider Integration

```bash
# Connect AWS
cirun cloud connect aws --access-key AKIXXXXXXXXX --secret-key KFCF3yi+df0n12345678AMASDFGHJ

# Connect Azure
cirun cloud connect azure \
  --subscription-id 31184337-0346-4782-ae59-eb185fd0cfa1 \
  --tenant-id a66e466d-698b-4a91-b9e3-949f9cc04f11 \
  --client-id 340d01fc-ba24-43ee-844e-d364899d29e7 \
  --client-secret KFCF3yi+df0cirunIsAwesomeIsntIt?n1DFGHJ

# Connect GCP
cirun cloud connect gcp --key-file /path/to/service-account-key.json
```

### Python Client Examples

```python
from cirun import Cirun

# Initialize client (pass token or set CIRUN_API_KEY environment variable)
cirun_client = Cirun(token='cirun-4cabcdbf-275c-4500-890d-712340663ddc')

# List all repositories
repos = cirun_client.get_repos()
print(repos)

# Activate a repository
cirun_client.set_repo('username/repo-name', active=True)

# Deactivate a repository
cirun_client.set_repo('username/repo-name', active=False)

# Connect cloud provider
cirun_client.connect_aws(
    access_key='AKIXXXXXXXXX',
    secret_key='KFCF3yi+df0n12345678AMASDFGHJ'
)
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CIRUN_API_KEY` | API key for authentication | (Required) |
| `CIRUN_API_URL` | Base URL for Cirun API | https://api.cirun.io/api/v1 |

## 📚 Documentation

For comprehensive documentation, visit:
- [Cirun Documentation](https://docs.cirun.io/)
- [Python Client API Reference](https://docs.cirun.io/python)
- [CLI Command Reference](https://docs.cirun.io/cli)

## 🔍 Troubleshooting

### Common Issues

- **Authentication Errors**: Ensure your API key is correctly set
- **Connection Issues**: Check your network connection to api.cirun.io
- **Permission Problems**: Verify you have the required permissions for the operation

### Debug Mode

For detailed logs:

```bash
cirun --debug repo list
```

## 💬 Support

Get help from our team and community:

- **Slack**: [Join our community](https://slack.cirun.io/)
- **Email**: support@cirun.io
- **GitHub Issues**: [Report bugs](https://github.com/cirun-io/cirun-py/issues)

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

We welcome contributions! Here's how:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🔄 Related Projects

- [cirun-agent](https://github.com/cirun-io/cirun-agent): Rust agent for on-premise runner provisioning
- [cirun-docs](https://github.com/cirun-io/cirun-docs): Documentation for the Cirun platform
