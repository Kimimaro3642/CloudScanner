# Project Progress

## Overview
This document tracks the progress of the CloudScanner project from start to current state. Updated as work is completed.

## Session 1: Project Foundation (January 9-12)

Project setup and initial infrastructure.

- Created project structure
- Set up directory layout for Python package
- Created 6 unit tests (all eventually passing)
- Set up test coverage reporting
- Created CI/CD workflows (tests.yml for automated testing, scan.yml for scheduled security scans)
- Initialized GitHub repository and pushed all files
- Created Dockerfile for containerisation
- Built Docker image successfully (cloudscanner:latest)
- Verified Docker image runs correctly

## Session 2: Documentation and Code Enhancement (January 30)

Deep dive into codebase with comprehensive documentation and feature additions.

### Codebase Understanding
- Documented all files and their purposes
- Analysed entry points (main.py, scan.py)
- Reviewed all three security check functions (NSG, Storage, KeyVault)
- Understood core utilities (model, clients, cvss, mitre, reporter)
- Reviewed test patterns and coverage
- Examined configuration files and CI/CD workflows

### Feature Additions
- Created test_reports.py script for generating sample security reports without Azure credentials
- Added MITRE ATT&CK technique mapping display to HTML reports
- Added CSS styling to HTML reports for better readability
- Implemented CVSS 3.1 scoring system (0.0-10.0 scale)
- Added colour-coded severity display to HTML reports (red for high, orange for medium, green for low)
- Updated all three check functions (nsg.py, storage.py, keyvault.py) to populate CVSS scores
- Verified all 6 unit tests still pass after CVSS integration
- Confirmed test_reports.py generates valid reports with CVSS scores

### Dependency Management
- Separated production and development dependencies
- Created requirements-dev.txt for testing tools (pytest, pytest-cov)
- Kept requirements.txt for production dependencies only
- Updated README.md with installation instructions for both files
- Documented reasoning for dependency separation in ISSUES.md

### Repository Cleanup
- Removed unnecessary configuration files (.flake8, .pylintrc)
- Removed redundant documentation files (ARCHITECTURE.md, CONTRIBUTING.md, SECURITY.md)
- Kept REFERENCE2.md as detailed technical reference for learning
- Restructured PROGRESS.md to session-based format
- Added category-based quick reference to ISSUES.md
- Documented all decisions and reasoning in tracking files

## Current Status

Code is complete and functional.

- 6 unit tests passing (NSG, Storage, KeyVault - 2 tests each)
- Test coverage at 47%
- No spurious or unused code
- All three check functions have CVSS 3.1 scoring
- HTML reports include MITRE mappings, CVSS scores, and color-coding
- JSON reports include all finding details
- Docker image builds and runs successfully
- Sample reports generate without Azure credentials needed

Documentation status.

- REFERENCE2.md: Detailed line-by-line breakdown of all code (working reference)
- REFERENCE.md: Simplified plain English version in progress (shows understanding)
- README.md: Complete with quick start and running instructions
- TESTING.md: Complete with test running guidance
- ISSUES.md: Complete with 12 resolved issues and lessons learned
- PROGRESS.md: Complete (this document)

## Next Phase

### Immediate: Additional Testing

- Expand test coverage beyond 47%
- Add integration tests for full end-to-end pipeline
- Test error handling (network failures, auth errors, missing resources)
- Add tests for report generation with edge cases
- Mock more complex Azure resource scenarios

### Terraform: Vulnerable Lab Creation

Create terraform/ directory with infrastructure-as-code for intentionally vulnerable Azure resources:

- **azure_vulnerable_lab.tf** - Misconfigured resources to test scanner against
  - NSG with world-accessible SSH (port 22) and RDP (port 3389)
  - Storage account with public blob container access enabled
  - Key Vault without purge protection enabled
- **variables.tf** - Configuration for lab setup (location, naming conventions, resource group)
- **outputs.tf** - Resource IDs and connection details for reference
- **terraform.tfvars** - Lab environment variables and naming

**Purpose:** Enable realistic testing by spinning up actual vulnerable resources, running scanner against them, then destroying to control costs.

**Workflow:**
```bash
terraform init
terraform plan
terraform apply  # Creates vulnerable resources
python scanner/src/main.py  # Scans them
terraform destroy  # Cleans up
```

**Benefits:**
- Tests scanner against real vulnerable configurations (not mocks)
- Demonstrates scanner effectiveness with actual Azure misconfigurations
- Infrastructure-as-Code documentation of what makes resources vulnerable
- Allows realistic reporting against genuine findings

### Live Azure Environment Testing

- Run scanner against real Azure resources with actual credentials
- Test all three check functions in production environment
- Verify report generation with real findings
- Validate CVSS scores and MITRE mappings in real-world context

### Final Capstone Deliverables

- Complete REFERENCE.md rewrite (learning and interpretation)
- Prepare final capstone report
- Code review and documentation polish

## Stretch Goals

### Scanner Deployment to Azure Container Instance

Use Terraform to automate scanner deployment to cloud:

- **azure_scanner_deployment.tf** - Azure Container Instance configuration
  - Container image from cloudscanner:latest Docker image
  - Environment variables for Azure credentials
  - Persistent storage for report output
- **variables.tf** - Deployment configuration (region, container specs, schedule)
- **outputs.tf** - Container details and access information

**Purpose:** Deploy scanner to Azure for scheduled automated scanning without local infrastructure.

**Benefits:**
- Scheduled security scans on a recurring basis
- Reports stored in Azure storage for centralized access
- No local machine required to run scanner
- Infrastructure-as-Code for reproducible deployments

### Multi-Cloud Support

**Google Cloud Platform (Primary)**
- Create check_gcp_compute.py for GCP Compute Engine security groups
- Create check_gcp_storage.py for GCS bucket access controls
- Create check_gcp_kms.py for Cloud KMS key rotation policies
- Update reporter to support "gcp" provider
- Add GCP credential handling in scan.py
- Create GCP client wrapper similar to AzureClients

**Amazon Web Services (Secondary)**
- Create check_aws_security_groups.py for EC2 security group rules
- Create check_aws_s3.py for S3 bucket public access
- Create check_aws_kms.py for KMS key policies
- Update reporter to support "aws" provider
- Add AWS credential handling

### Vulnerable Lab Creation with Terraform

Create terraform/ directory with:
- **azure_vulnerable_lab.tf** - Intentionally misconfigured Azure resources
  - NSG with world-accessible SSH/RDP
  - Storage account with public blob access
  - Key Vault without purge protection
- **variables.tf** - Configuration for lab setup
- **outputs.tf** - Resource IDs and connection details
- **terraform.tfvars** - Lab naming and location

**Purpose:** Spin up real vulnerable resources to test scanner against, then tear down to control costs.

**Usage:**
```bash
terraform init
terraform plan
terraform apply  # Creates vulnerable resources
python scanner/src/main.py  # Scans them
terraform destroy  # Cleans up
```

**Benefits:**
- Tests scanner against actual vulnerable configurations
- More realistic than mocked findings
- Demonstrates scanner effectiveness with real resources
- Infrastructure-as-Code documentation of vulnerabilities

## How to Run

Generate sample reports (no Azure credentials needed).

python test_reports.py

Run tests locally.

python -m pytest scanner/tests/ -v --cov=scanner/src

Build Docker image.

docker build -t cloudscanner:latest -f scanner/Dockerfile .

## Repository Information

GitHub: https://github.com/Kimimaro3642/CloudScanner
Last updated: January 30, 2026
Commits: 20+ (see git log for history)