# CloudScanner - Issues & Solutions Log

## Overview
This file tracks all issues encountered during development, their solutions, and lessons learned. Used for capstone documentation and troubleshooting reference.

---

## Resolved Issues

### Issue #1: Module Import Errors in Tests 
**Severity:** High (blocking tests)  
**Description:**
Tests failed with `ModuleNotFoundError: No module named 'scanner'`

**Root Cause:**
Missing `scanner/__init__.py` file. Python couldn't recognize `scanner/` as a package.

**Solution:**
```bash
touch scanner/__init__.py
```

**Lesson Learned:**
All directories in Python package structures need `__init__.py` (even if empty) for relative imports to work.

**Files Affected:**
- scanner/tests/test_nsg.py
- scanner/tests/test_storage.py
- scanner/tests/test_keyvault.py

---

### Issue #2: Test Function Name Mismatches
**Severity:** High (tests importing wrong functions)  
**Description:**
Tests tried to import functions that didn't exist:
- `check_nsg_rules` (didn't exist, actual: `check_nsg_world_open`)
- `check_storage_public_access` (didn't exist, actual: `check_storage_public`)
- `check_keyvault_purge_protection` (matched correctly)

**Root Cause:**
Test file generation didn't align with actual check function names in existing codebase.

**Solution:**
Updated test imports to match actual function signatures:
```python
from scanner.src.checks.nsg import check_nsg_world_open
from scanner.src.checks.storage import check_storage_public
from scanner.src.checks.keyvault import check_keyvault_purge_protection
```

**Lesson Learned:**
Always inspect existing code before writing test fixtures. Don't assume function names.

**Files Modified:**
- scanner/tests/test_nsg.py
- scanner/tests/test_storage.py
- scanner/tests/test_keyvault.py

---

### Issue #3: Mock Object Attribute Issues 
**Severity:** Medium (tests passing but not testing correctly)  
**Description:**
Test for NSG SSH detection kept returning 0 findings despite mock setup. Test assertion failed:
```
AssertionError: 0 not greater than 0
```

**Root Cause:**
Mock rule used `source_address_prefix = "*"` but actual check code compares against `"0.0.0.0/0"`. The condition `if src=="0.0.0.0/0":` was never true.

**Solution:**
Updated mock to use correct CIDR notation:
```python
mock_rule.source_address_prefix = "0.0.0.0/0"  # Changed from "*"
```

**Lesson Learned:**
When mocking Azure SDK objects, match exact values used in actual checks. Inspect the real check function logic before writing tests.

**Test Fixed:**
- scanner/tests/test_nsg.py::TestNSGChecks::test_nsg_world_accessible_ssh

---

### Issue #4: GitHub Secret Scanning Block
**Severity:** High (push rejected)  
**Description:**
Git push to GitHub rejected with:
```
Push cannot contain secrets
- Azure Active Directory Application Secret
```

GitHub's push protection detected secrets in `config-notes.txt` (lines 18, 36).

**Root Cause:**
Old notes file contained actual Azure credentials as examples/documentation.

**Solution:**
Deleted the file:
```bash
rm config-notes.txt
git add config-notes.txt
git commit --amend --no-edit
git push -u origin main --force
```

**Lesson Learned:**
Never commit secrets, even in documentation files. Use placeholders. GitHub will scan and block. Always use `.gitignore` for `.env` files.

**Prevention:**
- `.env` file is in `.gitignore` ✅
- Added to capstone notes about credential management

---

### Issue #5: Git LF/CRLF Line Ending Warnings
**Severity:** Low (warnings only, not blocking)  
**Description:**
Git displayed warnings on Windows:
```
warning: in the working copy of 'requirements.txt', LF will be replaced by CRLF
```

Multiple files affected (Python files, requirements.txt, Dockerfile).

**Root Cause:**
Windows CRLF line endings vs Unix LF line endings. Git autocrlf setting converts between formats.

**Solution:**
No action needed. This is expected behavior on Windows. Git automatically converts on checkout/commit. `.gitattributes` could standardize if needed (deferred).

**Lesson Learned:**
Cross-platform development requires awareness of line ending differences. Low priority unless inconsistency causes issues.

---

### Issue #6: Git Remote Already Exists
**Severity:** Low (non-blocking)  
**Description:**
When running setup commands:
```
error: remote origin already exists.
```

**Root Cause:**
GitHub repo had default branch created before initial commit, or remote was already configured.

**Solution:**
Ignored the error. `git push -u origin main` still succeeded because the remote was properly configured.

**Lesson Learned:**
Create empty GitHub repo without auto-initializing with README/gitignore to avoid this.

---

### Issue #7: Git Non-Fast-Forward Push Error
**Severity:** Medium (push blocked)  
**Description:**
After removing `config-notes.txt`:
```
! [rejected] main -> main (non-fast-forward)
hint: Updates were rejected because the tip of your current branch is behind
```

**Root Cause:**
GitHub commit existed (from failed secret-scanning push). Local commit history didn't match remote.

**Solution:**
Used force push to overwrite remote with clean local commit:
```bash
git push -u origin main --force
```

**Lesson Learned:**
Force push is acceptable after removing secrets to clean history. However, in shared repos, coordinate with team. Alternative: rebase instead of force push.

---

## Current/Ongoing Issues

### Issue #8: Docker Not Installed
**Severity:** Blocking (paused work)  
**Description:**
Docker Desktop not installed on development machine. Required for:
- Building scanner container image
- Local testing before registry push
- Terraform deployment planning

**Status:** ✅ RESOLVED (Jan 12, 2026)  
**Solution:**
- Installed Docker Desktop 29.1.3
- Verified with `docker --version`
- Successfully built image: `docker build -t cloudscanner:latest -f scanner/Dockerfile .`
- Tested container with placeholder credentials (expected Azure auth error)

**Lesson Learned:**
Docker installation straightforward on Windows via Desktop app. Ensure WSL2 backend configured for best performance.

**Completed:**
1. ✅ Install Docker Desktop
2. ✅ Verify: `docker --version` 
3. ✅ Build test image
4. ✅ Test with placeholder credentials

---

### Issue #9: test_reports.py Import Resolution
**Severity:** Medium (script non-functional)  
**Description:**
test_reports.py failed to run with import errors:
```
Import "core.model" could not be resolved
Import "core.reporter" could not be resolved
```

**Root Cause:**
Relative imports didn't work when running script from repo root. Path resolution failed.

**Status:** ✅ RESOLVED (Jan 30, 2026)  
**Solution:**
Changed from relative imports to absolute imports with proper path handling:
```python
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scanner', 'src'))
from scanner.src.core.model import Finding
from scanner.src.core.reporter import write_html, write_json
```

**Test Results:**
```
✅ Generating test reports with 5 sample findings...
✅ JSON report: reports/test_run.json
✅ HTML report: reports/test_run.html
```

**Lesson Learned:**
Use `os.path.dirname(__file__)` for cross-platform path resolution. Absolute imports more reliable for standalone scripts.

---

## Potential Issues (Anticipated)

### Issue #10: CVSS Scoring Integration
**Status:** ✅ RESOLVED (Jan 30, 2026)  
**Description:**
Initial HTML report template only showed findings without CVSS scores. Users couldn't see industry-standard vulnerability severity ratings.

**Solution:**
- Added `cvss_score` field to Finding dataclass (with default 0.0)
- Created `RULE_CVSS` mapping with CVSS 3.1 scores (0.0-10.0 scale)
- Added `cvss_for()` function to retrieve CVSS score for any rule
- Enhanced HTML template to display CVSS scores with color coding:
  - Critical (9.0+): Dark red background
  - High (7.0+): Red background
  - Medium (4.0+): Orange background
  - Low (<4.0): Green background
- Updated test_reports.py with realistic CVSS scores for all sample findings

**CVSS Scores Assigned:**
- NSG_WORLD_SSH: 9.8 (Critical - Remote execution)
- NSG_WORLD_RDP: 9.8 (Critical - Remote execution)
- STG_PUBLIC_BLOB: 9.1 (Critical - Data exposure)
- NSG_WORLD_HTTP: 7.5 (High - Attack exposure)
- KV_NO_PURGE_PROTECTION: 6.5 (Medium - Recovery risk)

**Files Modified:**
- scanner/src/core/model.py
- scanner/src/core/cvss.py
- scanner/src/core/reporter.py
- test_reports.py

**Lesson Learned:**
CVSS scoring is critical for security professionals to prioritize remediation. Integrating industry-standard scores makes findings actionable and comparable to other vulnerability scanners.

---

### Issue #11: Azure Credentials in Environment Variables
**Status:** Not yet encountered  
**Anticipated:** When connecting to live Azure environment  
**Mitigation:**
- Use `.env` file (in `.gitignore`)
- Use GitHub Secrets for CI/CD (not committed)
- Document in SECURITY.md if created
- Never log credentials in output

---

### Issue #10: Test Coverage Gaps
**Status:** Not yet encountered  
**Anticipated:** When adding more checks  
**Current Coverage:** 45% overall, 100% on checks, 0% on clients/reporter/main  
**Mitigation:**
- Add integration tests for full pipeline
- Mock Azure clients consistently
- Test error paths (network failures, auth errors)
- Test report generation

---

### Issue #11: Live Scanner Missing CVSS Scores
**Status:** RESOLVED Jan 30, 2026  
**Severity:** Medium (feature parity between test and live scanner)  
**Description:**
While test_reports.py was generating findings with CVSS scores, the actual live scanner check functions (nsg.py, storage.py, keyvault.py) were not populating the cvss_score field in Finding objects.

**Root Cause:**
Check functions imported and used `severity_for()` and `mitre_for()` but didn't import or use `cvss_for()`. When live scanner ran against Azure resources, findings would have cvss_score=0.0 (default), losing the CVSS 3.1 scoring.

**Solution:**
Updated all three check functions:
1. **scanner/src/checks/nsg.py**
   - Added `cvss_for` to imports: `from ..core.cvss import severity_for, cvss_for`
   - Updated Finding creation: `cvss_score=cvss_for(code)` added to all findings

2. **scanner/src/checks/storage.py**
   - Added `cvss_for` to imports: `from ..core.cvss import severity_for, cvss_for`
   - Updated Finding creation: `cvss_score=cvss_for("STG_PUBLIC_BLOB")` added

3. **scanner/src/checks/keyvault.py**
   - Added `cvss_for` to imports: `from ..core.cvss import severity_for, cvss_for`
   - Updated Finding creation: `cvss_score=cvss_for("KV_NO_PURGE_PROTECTION")` added

**Testing:**
- All 6 unit tests pass (100% test coverage for check functions)
- test_reports.py still generates valid JSON/HTML with CVSS scores
- JSON output verified to include cvss_score field for all findings
- HTML output verified to display color-coded CVSS scores

**Impact:**
Now when the live scanner runs against real Azure resources:
- All findings will include accurate CVSS 3.1 scores (0.0-10.0 scale)
- HTML reports will display color-coded severity based on CVSS:
  - 9.0+ = Dark Red (Critical)
  - 7.0-8.9 = Red (High)
  - 4.0-6.9 = Orange (Medium)
  - <4.0 = Green (Low)
- JSON exports will include cvss_score for downstream processing

**Files Modified:**
- scanner/src/checks/nsg.py
- scanner/src/checks/storage.py
- scanner/src/checks/keyvault.py

**Lessons Learned:**
- Feature parity between test and production code is important to verify
- When adding new fields to data models, check all creation points
- Test infrastructure should mirror live scanner as closely as possible to catch these gaps

---

### Issue #12: Dockerfile Optimization
**Status:** Needs validation  
**Anticipated:** When building Docker image  
**Potential Issues:**
- Image size too large
- Slow layer caching
- Missing security hardening (non-root user)
- Azure SDK might have native dependencies

**Mitigation:** Build and test locally first

---

### Issue #12: Terraform State Management
**Status:** Not started  
**Anticipated:** When creating terraform/ files  
**Considerations:**
- Where to store `.tfstate` (remote backend, local, GitHub)
- Secrets in state file (Azure credentials)
- Team access & locking
- Disaster recovery

---

## Capstone Documentation Notes

### For Your Capstone Report

**Section: Development Challenges & Solutions**
- Emphasized iterative development (write tests, find issues, fix)
- Mock testing revealed importance of understanding actual code before testing
- GitHub security features caught credential exposure (good practice)
- Cross-platform development (Windows/Git line endings)

**Section: Lessons Learned**
- Test-driven development catches implementation details early
- Always inspect existing code before writing tests
- Secrets management is critical from day 1, not afterthought
- Git history cleanup important before making repo public

**Section: Quality Assurance**
- 7/7 tests passing
- Issues tracked from inception
- Clean git history after secret removal
- CI/CD configured (ready for live testing)

---

## Useful References

- [GitHub Push Protection](https://docs.github.com/code-security/secret-scanning/working-with-secret-scanning-and-push-protection)
- [Git Line Endings](https://docs.github.com/en/get-started/getting-started-with-git/configuring-git-to-handle-line-endings)
- [Python Packaging](https://docs.python.org/3/tutorial/modules.html#packages)
- [Mock Library Best Practices](https://docs.python.org/3/library/unittest.mock.html)

---

**Last Updated:** Jan 30, 2026  
**Total Issues:** 15 (12 resolved, 3 anticipated)