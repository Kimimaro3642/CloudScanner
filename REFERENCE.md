# CloudScanner Reference Sheet
# Detailed explanation of every file in the project with context.
# Living document updated as project progresses and goals met.

1. Dependencies
2. Entry Point
3. Orchestration
4. Security Checks
    - NSG Check 
    - Storage Check
    - Key Vault Check
5. Core Utilities
    - Model
    - Clients
    - CVSS
    - MITRE
    - Reporter
6. Tests
7. Configuration Files
8. CI/CD Workflows

# 1. Dependencies (requirements.txt)
    - Purpose: Lists every Python library the scanner needs. `pip install -r requirements.txt` downloads and installs all needed libraries.
    - Versions are pinned for consistency.  Prevents breaking of functionality as design progresses.

## What's in use?
1. azure-identity==1.17.1
    - Standard azure library. Handles authentication.
    - issues temporary access token after providing tenantID, clientID and secret.
    - Used to query azure resources.

2. azure-mgmt-resource==23.1.0
    - Azure Resource management library.
    - Used to interact with resources in Azure.
    **NOTE: Not used very heavily currently as no production azure resources configured.  Only test creds but will be used a lot more as project develops to query live environments.**

3. azure-mgmt-network==25.3.0
    - Azure Network management library.
    - Used to list and work with networking resources (NSGs, virtual networks etc...)
    - Similar to resource library but specifically for networks.

4. azure-mgmt-storage==21.2.1
    - Azure Storage management library.
    - Used to list and work with storage accounts (blobs, files, tables, queues).
    - Gets properties of storage accounts, including blob access settings for storage test.

5. azure-mgmt-keyvault==10.3.0
    - Azure key vault management library.
    - Used to Work with key vaults (secrets, keys, certificates).
    - Lists all key vaults.
    - Reads vault properties.
    - Checks if purge protection is enabled for KV test.

6. jinja2==3.1.4
    - HTML template rendering engine.
    - Create HTML files from template. Fills in data from tests to create report.

7. cvss==3.1
    - CVSS (Common Vulnerability Scoring System) library.
    - Calculate and score vulnerability severity.
    **NOTE: Currently not using the full CVSS scoring yet.  Provisionally using hardcoded values to generate results in report**

8. requests==2.32.3
    - HTTP library for web requests.  
    - Send HTTP GET/POST/etc... requests to web services.
    - Installed indirectly as azure libraries require it.

# 2. Entry Point (main.py)

## What This File Does
Where everything starts. Executes first when `python scanner/src/main.py` runs.

## Breakdown (Line by Line)

1. import argparse
    - Import the argument parsing library.  
    - This library allows for command line arguments like `python main.py --out results.html`.

2. from .core import reporter
    - Import the reporter module.
    - Load the code for generating HTML and JSON reports.

3. from .scan import run_azure
    - Import the run_azure function. 
    - Load the function that orchestrates all the security checks from scanner.src.scan.py.

5. def main():
    - Define the main function.
    - This is the first code that runs.

6. ap=argparse.ArgumentParser()
    - Create an argument parser object to handle command line arguments. 

7. ap.add_argument("--out",default="reports/run.html")
    - Add an optional argument for output HTML file path.
    - Using this we can specify where to save the HTML report. If nothing specified use `reports/run.html` as default.

8. ap.add_argument("--json",default="reports/run.json")
    - Similar to the above, add an optional argument for output JSON file path.
    - Using this we can specify where to save the JSON report. If nothing specified use `reports/run.json` as default.

9. a=ap.parse_args()
    - Parses the command-line arguments.
    - Read what was typed on the command line and store it in variable `a`.

10. f=run_azure()
    - Call the run_azure function from scan.py.  
    - Carry out all the security checks (NSG, Storage, KeyVault currently) and get back a list of findings.
    **What Happens:**
     1. Grab Azure credentials from environment variables.
     2. Connect to Azure.
     3. Run all three checks.
     4. Return list of finding objects.
    **Result:** `f` contains all the vulnerabilities found.

11. reporter.write_json(f,a.json)  
    - Take the findings and write them as JSON to the path specified (or default).

12. reporter.write_html("azure",f,a.out)
    - Take the findings and save them as a pretty HTML report to the path specified (or default).
    **Parameters:**
    - `"azure"` - Cloud provider name (in future could be "gcp", "aws" too).
    - `f` - List of findings.
    - `a.out` - Output file path.

13. print("Done, findings:",len(f))
    - Print summary of vulns found to console.

14. if __name__=="__main__": main()
    - Run main() only if this file is run directly.  
    - This code only runs if `python main.py` is executed. It doesn't run if file imported in another script.

## **main.py flow**

- Run: python main.py --out results.html
- main() function starts
- Parse command-line arguments
- Call run_azure() to get findings
- Write JSON report
- Write HTML report
- Print "Done, findings: X"
- End

# 3. Orchestration (scan.py)

blah blah blah