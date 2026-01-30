# CloudScanner - Issues & Lessons Learned

Tracks problems encountered during development, how they were solved, and what was learned. This is the project's troubleshooting guide and knowledge base.

---

# Resolved Issues

## 1. Missing __init__.py Files

**Problem:**
Tests failed with `ModuleNotFoundError: No module named 'scanner'`. Python didn't recognize `scanner/` as a package.

**Why:**
Python needs `__init__.py` files (even if empty) in directories to treat them as packages. Without it, relative imports fail.

**Solution:**
Created `scanner/__init__.py` (empty file was sufficient).

**Plain English:**
Think of `__init__.py` as a "I'm a package" sign. Python sees the file and knows "this directory can be imported from".

---

## 2. Test Function Name Mismatches

**Problem:**
Tests tried to import functions that didn't exist:
- `check_nsg_rules` → actual: `check_nsg_world_open`
- `check_storage_public_access` → actual: `check_storage_public`

**Why:**
Test file was created without inspecting existing code first.

**Solution:**
Updated test imports to match actual function names:
```python
from scanner.src.checks.nsg import check_nsg_world_open
from scanner.src.checks.storage import check_storage_public
from scanner.src.checks.keyvault import check_keyvault_purge_protection
```

**Lesson:**
Always inspect existing code before writing tests. Don't assume function names.

---

## 3. Mock Objects Not Matching Reality

**Problem:**
NSG test returned 0 findings despite correct mock setup.

**Why:**
Mock used `source_address_prefix = "*"` but actual check compares against `"0.0.0.0/0"`. The condition never matched.

**Solution:**
Updated mock to use exact value from real code:
```python
mock_rule.source_address_prefix = "0.0.0.0/0"  # Instead of "*"
```

**Lesson:**
When mocking, match exact values used in the real check function. Inspect logic before writing tests.

---

## 4. GitHub Blocked Push (Secrets in Files)

**Problem:**
Git push rejected with: `Push cannot contain secrets - Azure Active Directory Application Secret`

**Why:**
Old `config-notes.txt` had example Azure credentials in it. GitHub's secret scanning caught it.

**Solution:**
Deleted the file and force-pushed clean history:
```bash
rm config-notes.txt
git push --force
```

**Lesson:**
Never commit secrets, even in documentation. Use placeholders. Always add `.env` to `.gitignore` from day one.

---

## 5. Git Line Ending Warnings (Windows)

**Problem:**
Git warnings: `warning: in the working copy of 'requirements.txt', LF will be replaced by CRLF`

**Why:**
Windows uses CRLF line endings, Unix uses LF. Git auto-converts between them on different systems.

**Solution:**
No action needed. This is normal on Windows. Git handles it automatically.

**Lesson:**
Cross-platform development (Windows/Mac/Linux) means awareness of line ending differences. Usually not a blocker.

---

## 6. Git Remote Already Exists Error

**Problem:**
Error: `remote origin already exists` when trying to set remote.

**Why:**
GitHub repo was pre-initialized or remote already configured.

**Solution:**
Ignored error. `git push` still succeeded because remote was properly configured.

**Lesson:**
Create empty GitHub repos without auto-initializing to avoid this.

---

## 7. Non-Fast-Forward Git Push Error

**Problem:**
Push rejected: `[rejected] main -> main (non-fast-forward)` after removing secrets.

**Why:**
Remote had a commit that local didn't match (from failed secret-scanning push).

**Solution:**
Used force push to overwrite remote with clean local history:
```bash
git push --force
```

**Lesson:**
Force push is acceptable to clean history after removing secrets. In shared repos, coordinate with team first.

---

## 8. Docker Desktop Not Installed

**Problem:**
Docker commands failed - Docker Desktop not installed.

**Status:** [RESOLVED]

**Solution:**
- Installed Docker Desktop 29.1.3
- Verified: `docker --version`
- Built test image successfully
- Tested with placeholder credentials

**Lesson:**
Docker installation on Windows via Desktop app is straightforward. Ensure WSL2 backend is configured.

---

## 9. test_reports.py Import Path Issues

**Problem:**
Script failed with import errors when running from repo root:
```
Import "core.model" could not be resolved
Import "core.reporter" could not be resolved
```

**Why:**
Relative imports don't work for standalone scripts. Python's path resolution failed.

**Status:** [RESOLVED]

**Solution:**
Used absolute imports with explicit path handling:
```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scanner', 'src'))
from scanner.src.core.model import Finding
from scanner.src.core.reporter import write_html, write_json
```

**Lesson:**
For standalone scripts, use `os.path.dirname(__file__)` to build paths. Absolute imports more reliable than relative.

---

## 10. CVSS Scoring Missing from Find Model

**Problem:**
HTML reports showed findings but without CVSS 3.1 severity scores.

**Status:** [RESOLVED]

**Solution:**
- Added `cvss_score` field to Finding class
- Created RULE_CVSS mapping with industry-standard scores (0.0-10.0 scale)
- Added `cvss_for()` function to look up scores
- Updated HTML template to display with color-coding:
  - Dark Red (9.0+): Critical
  - Red (7.0-8.9): High
  - Orange (4.0-6.9): Medium
  - Green (<4.0): Low

**CVSS Scores Used:**
- NSG_WORLD_SSH: 9.8 (Critical)
- NSG_WORLD_RDP: 9.8 (Critical)
- STG_PUBLIC_BLOB: 9.1 (Critical)
- NSG_WORLD_HTTP: 7.5 (High)
- KV_NO_PURGE_PROTECTION: 6.5 (Medium)

**Lesson:**
CVSS scoring is critical for security teams to prioritize remediation. Integrating industry-standard scores makes findings actionable and comparable.

---

## 11. Live Scanner Missing CVSS Scores

**Problem:**
Test reports had CVSS scores, but live scanner check functions (nsg.py, storage.py, keyvault.py) weren't populating cvss_score in findings.

**Why:**
Check functions used `severity_for()` and `mitre_for()` but didn't import or use `cvss_for()`.

**Status:** [RESOLVED]

**Solution:**
Updated all three check functions:

**nsg.py:**
- Added import: `from ..core.cvss import severity_for, cvss_for`
- Added to Finding: `cvss_score=cvss_for(code)`

**storage.py:**
- Added import: `from ..core.cvss import severity_for, cvss_for`
- Added to Finding: `cvss_score=cvss_for("STG_PUBLIC_BLOB")`

**keyvault.py:**
- Added import: `from ..core.cvss import severity_for, cvss_for`
- Added to Finding: `cvss_score=cvss_for("KV_NO_PURGE_PROTECTION")`

**Testing:**
All 6 unit tests pass. HTML and JSON reports include CVSS scores.

**Lesson:**
Ensure feature parity between test and live code. Check all object creation points when adding new fields.

---

# Key Lessons Learned

## Why Separate Requirements Files?

**Production** vs **Development** have different needs:

**requirements.txt (Production)**
- Azure SDKs, Jinja2, CVSS, requests
- Only what's needed to run scanner
- Smaller, fewer dependencies
- Faster Docker builds

**requirements-dev.txt (Development)**
- pytest, pytest-cov (testing tools)
- Only needed when developing
- Separate so production stays lean

**Usage:**
```bash
# Production only
pip install -r requirements.txt

# Development (tests)
pip install -r requirements.txt -r requirements-dev.txt
```

**Lesson:**
Separating dependencies is industry best practice. Keeps production deployments lightweight.

---

## Why Remove Linting Configuration?

**Linters** (flake8, pylint) check code **style**, not **functionality**:
- Variable naming: `x=5` should be `x = 5`
- Line length: "Should be <100 characters"
- Generate "code quality scores"

**For Capstone Projects, what matters:**
- Code works (6/6 tests passing)
- Documented (REFERENCE.md explains everything)
- Understandable (clear variable names, readable logic)
- Demonstrates knowledge

**What doesn't matter:**
- Perfect PEP 8 compliance (style rules)
- Code quality scores (matters for production)
- Linting tool configurations (adds noise)

**Lesson:**
For capstone, focus on functionality and documentation. Style enforcement is for production codebases.

---

## Why Keep REFERENCE2.md?

**REFERENCE2.md** is your detailed working reference - comprehensive line-by-line breakdown.

**REFERENCE.md** is your simplified capstone version - shows understanding.

Both serve purposes:
- REFERENCE2.md: Source material for learning
- REFERENCE.md: Your interpretation (demonstrates understanding)

**Workflow:**
1. Learn from REFERENCE2.md details
2. Simplify and rewrite for REFERENCE.md
3. Your simplified version shows you've internalized the code

---

## Repository Cleanup for Capstone

**Files Deleted:**
- ARCHITECTURE.md (content merged into REFERENCE.md)
- CONTRIBUTING.md (not relevant for capstone)
- SECURITY.md (not needed yet)

**Reasoning:**
One comprehensive REFERENCE.md is better than multiple scattered docs. Cleaner repository makes code easier to review.

**Lesson:**
For capstone projects: "Keep what demonstrates understanding, remove what adds noise."

---

## Dependency Management Misconception

**Common Mistake:**
"If I have a .coverage file, pytest must be installed"

**Reality:**
.coverage is an **output file** (test report data), not the tool itself. Having data ≠ having the tool.

**Correct Approach:**
Always declare packages in requirements.txt or requirements-dev.txt. Files document what tools are needed.

**Lesson:**
Artifact files (output data) don't mean tools are installed. Explicitly declare all dependencies.

---

# Future Considerations

### Terraform State Management (Not Started)
When creating infrastructure code:
- Where to store .tfstate files
- How to protect secrets in state
- Team access and locking
- Disaster recovery planning

### Live Azure Testing (Not Started)
When running against real Azure resources:
- Test with actual credentials
- Verify all three checks work end-to-end
- Confirm report generation with real findings
- Document any Azure-specific issues

### Docker Image Optimization (Needs Testing)
Potential improvements:
- Reduce image size
- Improve layer caching
- Add security hardening (non-root user)
- Test with large subscriptions

---

**Last Updated:** January 30, 2026  
**Total Issues Resolved:** 11  
**Status:** All known issues addressed
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
**Total Issues:** 16 (12 resolved, 4 anticipated)

---

## Lessons Learned - Dependencies

### Why .coverage File Didn't Mean pytest Was Installed
**Common Misconception:** Having a `.coverage` file doesn't mean pytest/pytest-cov packages are installed.

**Explanation:**
- `.coverage` is an **artifact/output file** - data created by pytest-cov after tests run
- It's like a test report - tells you results, but doesn't include the tools that created it
- The actual packages must be declared in `requirements.txt` or `pyproject.toml`
- Simply having the data file doesn't auto-install the packages

**Solution Implemented:** Separate dependency files (best practice):
- `requirements.txt` - Production only (Azure SDKs, Jinja2, CVSS, requests)
- `requirements-dev.txt` - Testing tools (pytest, pytest-cov)

**Usage:**
```bash
# Production only
pip install -r requirements.txt

# Production + development
pip install -r requirements.txt -r requirements-dev.txt

# Or in one command
pip install -r requirements.txt -r requirements-dev.txt
```

**Benefits:**
- Production deployments stay lightweight (fewer dependencies)
- Developers/CI/CD can easily install test tools
- Clear separation of concerns
- Industry best practice

Updated in this session: Created requirements-dev.txt and separated dependencies properly.

---

## Lessons Learned - Code Quality Tools vs. Capstone Requirements

### Why Remove Linting Tools (.flake8, .pylintrc)?

**Context:**
Project initially included code linting configuration files (.flake8, .pylintrc) which enforce PEP 8 style compliance. After reviewing capstone requirements, these were removed.

**What Linters Do:**
- Check code **style** (variable naming conventions, line length, spacing)
- Example violations: `x=5` (should be `x = 5`), lines >79 characters
- Provide "code quality scores" (e.g., 9.2/10 rating)
- Focus on **how code looks**, not **if it works**

**For a Capstone Project, What Actually Matters:**
- Functional - Code works, tests pass (6/6 passing)
- Documented - Clear explanation of what code does (REFERENCE.md)
- Understandable - Variable names are clear, logic is readable
- Demonstrated Knowledge - Shows you understand the code

**What doesn't matter:**
- Perfect PEP 8 compliance (style enforcement)
- Code quality scores (important for production codebases)
- Linting tool configurations (adds noise without value)

**Analogy:**
Writing an essay for a class:
- What matters: Good content, clear organization, demonstrates understanding
- What doesn't: Exactly 1.5 line spacing vs 1.25, perfect margins

**Decision Made:**
Removed `.flake8` and `.pylintrc` to:
1. Reduce repository noise
2. Focus attention on actual code and documentation
3. Simplify capstone submission
4. Make code quality about functionality, not style enforcement

**If Needed Later:**
Can be added back in 30 seconds:
```bash
pip install flake8
flake8 scanner/src/
```

---

## Lessons Learned - Repository Simplification for Capstone

### Why Remove Non-Essential Documentation Files?

**Files Deleted:**
- `ARCHITECTURE.md` - High-level design overview
- `CONTRIBUTING.md` - Contribution guidelines
- `SECURITY.md` - Security policy

**Reasoning:**
For a capstone project submission:
- One comprehensive REFERENCE.md is better than multiple docs
- Contribution guidelines not relevant (not an open-source project)
- Security policy not needed (capstone, not production)
- Cleaner repository = easier for reviewers to focus on actual code

**Decision Made:**
Content from these files that was valuable was integrated into:
1. **REFERENCE.md** - Comprehensive code documentation (your rewrite)
2. **README.md** - Quick start and running instructions
3. **ISSUES.md** - Lessons learned section

**Result:**
- Removed 5 non-essential files
- Created focused, single-source-of-truth documentation
- Repository is cleaner, easier to navigate
- REFERENCE2.md restored as working reference document

### Key Principle for Capstone Projects
**"Keep what demonstrates understanding, remove what adds noise."**

For this project:
- Keep: Working code, tests, documentation you wrote
- Remove: Configuration files, tools that don't add value to demo
- Document: Your decisions and reasoning (like this lesson)

---

## Documentation Workflow - REFERENCE.md vs REFERENCE2.md

### Purpose of Each File

**REFERENCE2.md** - Working Reference Document
- **Audience:** You (for learning and interpretation)
- **Content:** Detailed, line-by-line breakdown of every file
- **Format:** Technical, comprehensive, in-depth explanations
- **Use:** Source material for learning and cross-referencing
- **Updates:** Add new details as you discover them

**REFERENCE.md** - Simplified Capstone Reference
- **Audience:** Capstone reviewers, project readers
- **Content:** Distilled, plain-English explanations
- **Format:** Simplified, readable, demonstrates understanding
- **Use:** Your interpretation and simplified version
- **Updates:** Continuously refined from REFERENCE2.md

### Workflow
1. **Learn from REFERENCE2.md** - Read detailed breakdowns
2. **Interpret & Simplify** - Rewrite in your own words for REFERENCE.md
3. **Demonstrate Understanding** - Your simplified version shows you've internalized the code
4. **Keep Both** - Reference2 stays as detailed reference, Reference becomes simplified version

### Example
**REFERENCE2.md (detailed):**
```
The cvss_for() function takes a rule code as input and returns the corresponding 
CVSS 3.1 score by looking it up in the RULE_CVSS dictionary. If the rule code 
is not found in the dictionary, it returns 0.0 as a default value.
```

**REFERENCE.md (simplified):**
```
The cvss_for() function looks up a rule code and returns its CVSS score. 
If the rule isn't found, it returns 0.0.
```

Both serve a purpose - REFERENCE2.md helps you learn, REFERENCE.md shows you understand!