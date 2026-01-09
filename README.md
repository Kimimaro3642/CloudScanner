# Azure Cloud Security Scanner

A Python-based security scanner that audits Azure resources for vulnerabilities and misconfigurations.

## Features

- **NSG Security Rules** - Detects world-accessible ports (SSH, RDP, HTTP)
- **Storage Account Access** - Identifies publicly accessible blob containers
- **Key Vault Protection** - Checks for disabled purge protection
- **MITRE ATT&CK Mapping** - Correlates findings with threat tactics
- **HTML & JSON Reports** - Generates actionable security reports

## Quick Start

### Prerequisites
- Python 3.9+
- Azure subscription with credentials
- Virtual environment activated

### Installation

```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (macOS/Linux)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file with your Azure credentials:

```env
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
AZURE_TENANT_ID=your-tenant-id
```

### Running the Scanner

```bash
python scanner/src/main.py
```

Reports generated in:
- `reports/scan_report.html`
- `reports/scan_report.json`

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=scanner/src
```

## Code Quality

```bash
# Lint with pylint
pylint scanner/src/

# Format check with flake8
flake8 scanner/src/
```

## Project Structure

```
scanner/
├── src/
│   ├── main.py
│   ├── scan.py
│   ├── checks/
│   │   ├── nsg.py
│   │   ├── storage.py
│   │   └── keyvault.py
│   └── core/
│       ├── model.py
│       ├── clients.py
│       ├── mitre.py
│       ├── cvss.py
│       └── reporter.py
├── tests/
│   ├── test_all.py
│   └── test_*.py
└── reports/
```

## License

MIT