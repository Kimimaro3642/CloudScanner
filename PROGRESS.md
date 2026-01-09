# Project Progress

## Completed
- ✅ Project scaffold & structure
- ✅ Simulated unit tests (7 passing)
- ✅ CI/CD workflows setup
- ✅ GitHub repo created
- ✅ Dockerfile created (improved version in scanner/Dockerfile)

## Current Phase
- ⏳ **PAUSED: Docker Desktop installation** (rebooting machine)
- Next: Build Docker image locally
- Then: Create Terraform code for deployment

## Waiting On
- Docker Desktop install + restart
- Verify `docker --version` works
- Build image: `docker build -t cloudscanner:latest -f scanner/Dockerfile .`

## Future Phases
- [ ] Terraform code (main.tf, variables.tf, etc.)
- [ ] CI/CD pipeline for Docker build + Terraform deploy
- [ ] Live Azure lab environment testing
- [ ] Additional checks (GCP, AWS)
- [ ] Final capstone report

## Key Commands
```bash
# Verify Docker
docker --version

# Build image (after Docker installed)
docker build -t cloudscanner:latest -f scanner/Dockerfile .

# Run tests
python -m pytest scanner/tests/ -v

# Push code
git add -A && git commit -m "message" && git push
```

## Session Notes
- Started: Jan 9, 2026
- GitHub: https://github.com/Kimimaro3642/CloudScanner
- Dockerfile updated with improvements
- Next session: Continue from Docker build step