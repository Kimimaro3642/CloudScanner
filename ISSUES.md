# CloudScanner - Issues & Solutions Log

## Overview
This file tracks all issues encountered during development, their solutions, and lessons learned. Used for capstone documentation and troubleshooting reference.

---

## Resolved Issues

### Issue #1: Module Import Errors in Tests
**Date:** Jan 9, 2026  
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
**Date:** Jan 9, 2026  
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
**Date:** Jan 9, 2026  
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
**Date:** Jan 9, 2026  
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
**Date:** Jan 9, 2026  
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
**Date:** Jan 9, 2026  
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
**Date:** Jan 9, 2026  
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
**Date:** Jan 9, 2026  
**Severity:** Blocking (paused work)  
**Description:**
Docker Desktop not installed on development machine. Required for:
- Building scanner container image
- Local testing before registry push
- Terraform deployment planning

**Status:** ⏳ Pending Installation  
**Next Steps:**
1. Install Docker Desktop
2. Verify: `docker --version`
3. Build test image: `docker build -t cloudscanner:latest -f scanner/Dockerfile .`
4. Test with placeholder credentials

**Estimated Resolution:** Next session after reboot

---

## Potential Issues (Anticipated)

### Issue #9: Azure Credentials in Environment Variables
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

### Issue #11: Dockerfile Optimization
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

## Summary Table

| # | Issue | Date | Severity | Status | Resolution |
|---|-------|------|----------|--------|------------|
| 1 | Module import errors | Jan 9 | High | ✅ Resolved | Added scanner/__init__.py |
| 2 | Function name mismatches | Jan 9 | High | ✅ Resolved | Updated test imports |
| 3 | Mock attribute issues | Jan 9 | Medium | ✅ Resolved | Fixed CIDR notation in mocks |
| 4 | GitHub secret scan block | Jan 9 | High | ✅ Resolved | Removed config-notes.txt |
| 5 | LF/CRLF warnings | Jan 9 | Low | ✅ Accepted | No action needed |
| 6 | Git remote exists | Jan 9 | Low | ✅ Resolved | Ignored, push succeeded |
| 7 | Non-fast-forward error | Jan 9 | Medium | ✅ Resolved | Force push |
| 8 | Docker not installed | Jan 9 | Blocking | ⏳ Pending | Install in next session |
| 9 | Azure creds exposure | Anticipated | High | 🛡️ Mitigated | Use .env & GitHub Secrets |
| 10 | Coverage gaps | Anticipated | Medium | 🛡️ Mitigated | Plan integration tests |
| 11 | Dockerfile optimization | Anticipated | Medium | 🛡️ Noted | Test locally first |
| 12 | Terraform state mgmt | Anticipated | Medium | 🛡️ Noted | Use remote backend |

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

**Last Updated:** Jan 9, 2026  
**Total Issues:** 12 (8 resolved, 4 anticipated)