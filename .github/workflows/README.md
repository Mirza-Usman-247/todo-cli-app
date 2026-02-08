# GitHub Actions Workflows (T108-T113)

This directory contains CI/CD workflows for the Todo App Phase 5 deployment.

## Workflows

### 1. Build and Push Docker Images (`build-and-push.yml`)
- **Trigger**: Push to `main`/`develop`, tags, pull requests
- **Purpose**: Build and push Docker images to Oracle Container Image Registry (OCIR)
- **Jobs**:
  - `build-backend`: Build and push backend image
  - `build-frontend`: Build and push frontend image
  - `notify`: Send build status notifications

### 2. Deploy to OKE (`deploy-oke.yml`)
- **Trigger**: Successful build workflow, manual dispatch
- **Purpose**: Deploy application to Oracle Kubernetes Engine
- **Jobs**:
  - `deploy`: Deploy using Helm, run smoke tests
  - `rollback`: Automatic rollback on failure

### 3. Integration Tests (`integration-tests.yml`)
- **Trigger**: Pull requests, pushes, manual dispatch
- **Purpose**: Run comprehensive test suite
- **Jobs**:
  - `unit-tests`: Python unit tests with coverage
  - `lint`: Code linting (ruff, black, mypy)
  - `integration-tests`: Integration tests with Redis/Kafka
  - `e2e-tests`: End-to-end tests on Minikube
  - `security-scan`: Trivy vulnerability scanning

## Required Secrets (T108)

Configure these secrets in your GitHub repository settings:

### OCI Authentication
```
OCI_CLI_USER=<oci-user-ocid>
OCI_CLI_TENANCY=<oci-tenancy-ocid>
OCI_CLI_FINGERPRINT=<oci-api-key-fingerprint>
OCI_CLI_KEY_CONTENT=<oci-api-private-key-contents>
OCI_REGION=us-ashburn-1
OCI_TENANCY_NAMESPACE=<tenancy-namespace>
```

### OCIR (Oracle Container Image Registry)
```
OCIR_USERNAME=<tenancy-namespace>/<oci-username>
OCIR_AUTH_TOKEN=<oci-auth-token>
```

### OKE Cluster
```
OKE_CLUSTER_ID=<oke-cluster-ocid>
```

### Application Secrets (Optional)
```
DATABASE_PASSWORD=<production-db-password>
REDIS_PASSWORD=<redis-password>
KAFKA_SASL_USERNAME=<kafka-username>
KAFKA_SASL_PASSWORD=<kafka-password>
```

## Setup Instructions

1. **Generate OCI API Key**:
   ```bash
   openssl genrsa -out ~/.oci/oci_api_key.pem 2048
   openssl rsa -pubout -in ~/.oci/oci_api_key.pem -out ~/.oci/oci_api_key_public.pem
   ```

2. **Add public key to OCI**:
   - Navigate to: User Settings → API Keys → Add API Key
   - Upload `oci_api_key_public.pem`
   - Copy the fingerprint

3. **Generate OCIR Auth Token**:
   - Navigate to: User Settings → Auth Tokens → Generate Token
   - Copy the token immediately (cannot be retrieved later)

4. **Add secrets to GitHub**:
   - Repository Settings → Secrets and variables → Actions
   - Add each secret listed above

5. **Update values-oke.yaml**:
   ```yaml
   backend:
     image:
       repository: <region>.ocir.io/<tenancy-namespace>/todo-backend
   ```

## Workflow Behavior

### Pull Requests
- ✅ Build images (no push)
- ✅ Run unit tests
- ✅ Run linters
- ✅ Run integration tests
- ✅ Security scan

### Push to `develop`
- ✅ Build and push images with `develop` tag
- ✅ Deploy to staging environment
- ✅ Run smoke tests

### Push to `main`
- ✅ Build and push images with `latest` tag
- ✅ Deploy to production environment
- ✅ Run full E2E tests
- ✅ Automatic rollback on failure

### Tags (`v*.*.*`)
- ✅ Build and push images with semver tags
- ✅ Create GitHub release (if configured)

## Manual Deployment

Trigger deployment manually via GitHub UI:
1. Actions → Deploy to OKE → Run workflow
2. Select environment (staging/production)
3. Click "Run workflow"

## Monitoring Deployments

View deployment status:
```bash
# Check workflow runs
gh run list --workflow=deploy-oke.yml

# View specific run
gh run view <run-id>

# Watch logs
gh run watch <run-id>
```

## Troubleshooting

### Build Failures
- Check OCIR credentials
- Verify Docker context paths
- Review build logs

### Deployment Failures
- Check OKE cluster access
- Verify kubectl configuration
- Review Helm chart values
- Check pod logs: `kubectl logs -l app=backend -c backend`

### Test Failures
- Review test logs in Actions
- Check service health: `kubectl get pods`
- Verify Dapr components: `kubectl get components`

## Best Practices

1. **Never commit secrets** to the repository
2. **Test in staging** before production deployment
3. **Tag releases** using semantic versioning
4. **Monitor deployments** and set up alerts
5. **Review security scan results** before merging

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [OCI CLI Configuration](https://docs.oracle.com/en-us/iaas/Content/API/Concepts/sdkconfig.htm)
- [OCIR Documentation](https://docs.oracle.com/en-us/iaas/Content/Registry/home.htm)
- [Helm Documentation](https://helm.sh/docs/)
