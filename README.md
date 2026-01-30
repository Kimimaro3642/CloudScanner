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
- `reports/run.html` - Formatted HTML report
- `reports/run.json` - Structured JSON findings

### Generate Test Reports

To see what reports look like WITHOUT needing real Azure credentials:

```bash
# Generate sample findings and reports
python test_reports.py
```

This creates:
- `reports/test_run.html` - Example HTML report with sample findings
- `reports/test_run.json` - Example JSON output

Then view the HTML report:
```bash
# Windows
start reports/test_run.html

# macOS/Linux
open reports/test_run.html
```

## Testing

```bash
# Run unit tests
pytest scanner/tests/

# Run with coverage report
pytest scanner/tests/ --cov=scanner/src --cov-report=html

# View coverage in browser
start htmlcov/index.html
```

## Code Quality

```bash
# Lint with pylint
pylint scanner/src/

# Format check with flake8
flake8 scanner/src/
```

## Documentation

- **[REFERENCE.md](REFERENCE.md)** - Comprehensive line-by-line explanation of all code
- **[REFERENCE2.md](REFERENCE2.md)** - Backup copy of reference documentation  
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design and component overview
- **[TESTING.md](TESTING.md)** - Detailed testing guide