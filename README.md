# Azure Cloud Security Scanner

A Python-based security scanner that audits Azure resources for vulnerabilities and misconfigurations.

## What This Scanner Does

The scanner checks three categories of Azure security misconfigurations.

Network Security Groups
- Detects security group rules that allow world-accessible ports (SSH on 22, RDP on 3389, HTTP on 80)

Storage Accounts
- Identifies storage accounts with public blob container access enabled

Key Vaults
- Checks for key vaults that do not have purge protection enabled

Each finding includes CVSS 3.1 scoring (industry standard severity rating) and MITRE ATT&CK technique mapping.

## Quick Start

Prerequisites.
- Python 3.9 or later
- Azure subscription
- Azure credentials (subscription ID, client ID, secret, tenant ID)

Installation.

Create and activate a virtual environment.

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

Install dependencies.

```bash
# Production dependencies only
pip install -r requirements.txt

# Add these if you want to run tests
pip install -r requirements-dev.txt
```

Configure Azure credentials.

Create a file named `.env` in the project root with your Azure details.

```
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
AZURE_TENANT_ID=your-tenant-id
```

## Running the Scanner

Option 1: Using Python directly.

Run the scanner with default settings (outputs to reports/run.html and reports/run.json).

```bash
python scanner/src/main.py
```

Run with custom output paths.

```bash
python scanner/src/main.py --out my_report.html --json my_findings.json
```

Option 2: Using Docker.

Build the Docker image.

```bash
docker build -t cloudscanner:latest -f scanner/Dockerfile .
```

Run the container with your Azure credentials passed as environment variables.

```bash
docker run -e AZURE_SUBSCRIPTION_ID=your-id \
  -e AZURE_CLIENT_ID=your-client \
  -e AZURE_CLIENT_SECRET=your-secret \
  -e AZURE_TENANT_ID=your-tenant \
  -v $(pwd)/reports:/app/reports \
  cloudscanner:latest
```

Option 3: Generate sample reports (no Azure credentials needed).

Use this to see what reports look like without Azure access.

```bash
python test_reports.py
```

This creates sample findings and generates reports/test_run.html and reports/test_run.json.

## Report Format

HTML Reports
- Color-coded severity (red for high, orange for medium, green for low)
- CVSS 3.1 scores with severity coloring
- MITRE ATT&CK technique mappings
- Service, resource, and rule information
- References to documentation

JSON Reports
- Structured format suitable for processing
- Contains all finding details
- CVSS scores included
- Can be imported into other tools

## Testing

Run the unit tests to verify the scanner works.

```bash
python -m pytest scanner/tests/ -v
```

Run with coverage report.

```bash
python -m pytest scanner/tests/ -v --cov=scanner/src --cov-report=html
```

## Documentation

- **[REFERENCE.md](REFERENCE.md)** - Comprehensive line-by-line explanation of all code
- **[REFERENCE2.md](REFERENCE2.md)** - Detailed technical reference
- **[TESTING.md](TESTING.md)** - Detailed testing guide
- **[PROGRESS.md](PROGRESS.md)** - Project progress and status
- **[ISSUES.md](ISSUES.md)** - Known issues and solutions