# GitHub Actions Secrets Required

To use the Docker build and push workflow, you need to configure the following secrets in your GitHub repository:

## Navigate to Repository Settings

1. Go to your repository on GitHub
2. Click on **Settings**
3. In the left sidebar, click on **Secrets and variables** → **Actions**
4. Click **New repository secret**

## Required Secrets

### 1. OCI_USERNAME
- **Name**: `OCI_USERNAME`
- **Value**: Your OCI username in format: `<tenancy-namespace>/<username>`
  - Example: `ax1cmfkxkbut/oracleidentitycloudservice/your.email@example.com`
  - Or: `ax1cmfkxkbut/your-oci-username`

### 2. OCI_AUTH_TOKEN
- **Name**: `OCI_AUTH_TOKEN`
- **Value**: Your OCI Auth Token

#### How to Generate OCI Auth Token:

1. Log in to OCI Console
2. Click on your **Profile icon** (top right)
3. Click on your **username**
4. Scroll down to **Resources** section on the left
5. Click **Auth Tokens**
6. Click **Generate Token**
7. Give it a description (e.g., "GitHub Actions")
8. Click **Generate Token**
9. **Copy the token immediately** (you won't be able to see it again)
10. Paste it as the `OCI_AUTH_TOKEN` secret in GitHub

## Verification

After adding the secrets, you should see them listed (values will be hidden):
- `OCI_USERNAME`
- `OCI_AUTH_TOKEN`

## Trigger the Workflow

The workflow will automatically run when you:
- Push to `main` or `frontend-backend-integration` branches
- Manually trigger it from the Actions tab

## Manual Trigger

1. Go to **Actions** tab in your repository
2. Click on **Build and Push Docker Images to OCI** workflow
3. Click **Run workflow** button
4. Select the branch
5. Click **Run workflow**

## Expected Output

After successful execution, your images will be available at:
- Backend: `ax1cmfkxkbut.ocir.io/ax1cmfkxkbut/ranga-tech/dev/app-1:latest`
- Frontend: `ax1cmfkxkbut.ocir.io/ax1cmfkxkbut/ranga-tech/dev/app-2:latest`

## Troubleshooting

### Authentication Failed
- Verify your OCI_USERNAME format is correct
- Ensure your OCI_AUTH_TOKEN is valid and not expired
- Check that you have permissions to push to the repositories

### Repository Not Found
- Ensure the repositories exist in OCIR
- Create them through OCI Console if needed
- Verify the namespace and repository paths are correct

### Build Failed
- Check the workflow logs in the Actions tab
- Ensure Dockerfile syntax is correct
- Verify all required files are in the repository
