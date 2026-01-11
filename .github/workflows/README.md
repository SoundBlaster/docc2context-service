# GitHub Actions CI/CD Workflow

This directory contains the GitHub Actions workflow configuration for the DocC2Context Service project.

## Workflow Overview

The CI/CD pipeline is defined in `.github/workflows/ci-cd.yml` and includes the following stages:

### 1. Validation Stage
- **Trigger**: Runs on every push and pull request to the `main` branch
- **Purpose**: Validates the project structure, dependencies, and configuration
- **Actions**:
  - Runs the comprehensive validation script (`scripts/validate.py`)
  - Checks for errors and warnings
  - Fails the build if critical errors are found

### 2. Testing Stage
- **Trigger**: Runs after successful validation
- **Purpose**: Executes automated tests
- **Actions**:
  - Installs test dependencies
  - Runs pytest with verbose output
  - Reports test results

### 3. Build Stage
- **Trigger**: Runs after successful tests (on `main` branch only)
- **Purpose**: Builds and publishes Docker image
- **Actions**:
  - Logs in to Docker Hub (using secrets)
  - Builds Docker image
  - Pushes image to Docker Hub (on `main` branch only)

### 4. Deployment Stage
- **Trigger**: Runs after successful build (on `main` branch only)
- **Purpose**: Deploys to production
- **Actions**:
  - Executes deployment commands
  - Currently includes placeholder - customize with your deployment process

## Requirements

### GitHub Secrets
To use this workflow, you need to configure the following secrets in your GitHub repository:

1. **DOCKER_HUB_USERNAME**: Your Docker Hub username
2. **DOCKER_HUB_TOKEN**: Your Docker Hub access token (with push permissions)

### Repository Structure
The workflow expects the following structure:
```
docc2context-service/
├── .github/
│   └── workflows/
│       └── ci-cd.yml
├── scripts/
│   └── validate.py
├── requirements.txt
├── Dockerfile
└── tests/
```

## Customization

### Deployment Configuration
Edit the `deploy` job in `ci-cd.yml` to include your actual deployment commands. Example:

```yaml
- name: Deploy to production server
  run: |
    ssh user@your-server.com "docker pull ${{ secrets.DOCKER_HUB_USERNAME }}/docc2context-service:latest"
    ssh user@your-server.com "docker-compose down && docker-compose up -d"
    ssh user@your-server.com "docker system prune -f"
```

### Additional Jobs
You can add more jobs to the workflow as needed:
- Code quality checks (linting, formatting)
- Security scanning
- Integration tests
- Notification steps

## Usage

### Manual Trigger
You can manually trigger the workflow:
1. Go to the "Actions" tab in your GitHub repository
2. Select the "CI/CD Pipeline" workflow
3. Click "Run workflow"
4. Select the branch and click "Run workflow"

### Monitoring
Monitor workflow runs:
1. Go to the "Actions" tab
2. Click on a workflow run to see detailed logs
3. Check each job's output for errors or warnings

## Troubleshooting

### Common Issues

1. **Validation Failures**:
   - Check the validation script output
   - Fix any configuration or dependency issues
   - Ensure all required files are present

2. **Docker Build Failures**:
   - Verify Dockerfile syntax
   - Check for missing build dependencies
   - Ensure Docker Hub credentials are correct

3. **Test Failures**:
   - Run tests locally first
   - Check test dependencies
   - Verify test environment matches production

### Debugging
Use the GitHub Actions logs to debug issues:
- Click on failed jobs to see detailed error messages
- Check the "Annotations" section for specific warnings
- Download workflow artifacts if available

## Best Practices

1. **Keep workflows fast**: Optimize validation and test steps
2. **Use caching**: Cache dependencies between runs
3. **Secure secrets**: Never hardcode credentials in workflow files
4. **Test locally**: Run validation and tests locally before pushing
5. **Monitor regularly**: Check workflow runs for unexpected failures

## Support

For issues with GitHub Actions:
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Community Forum](https://github.community/)
- [GitHub Support](https://support.github.com/)