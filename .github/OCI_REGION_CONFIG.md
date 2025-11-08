# OCI Region Configuration

## Important: OCI Container Registry URL Format

The correct format for OCI Container Registry is:
```
<region-code>.ocir.io
```

**NOT**: `<namespace>.ocir.io`

## Common OCI Regions

| Region Name | Region Code | Registry URL |
|------------|-------------|--------------|
| US East (Ashburn) | `iad` | `iad.ocir.io` |
| US West (Phoenix) | `phx` | `phx.ocir.io` |
| Germany Central (Frankfurt) | `fra` | `fra.ocir.io` |
| UK South (London) | `lhr` | `lhr.ocir.io` |
| Canada Southeast (Toronto) | `yyz` | `yyz.ocir.io` |
| Japan East (Tokyo) | `nrt` | `nrt.ocir.io` |
| South Korea Central (Seoul) | `icn` | `icn.ocir.io` |
| Australia East (Sydney) | `syd` | `syd.ocir.io` |
| Brazil East (Sao Paulo) | `gru` | `gru.ocir.io` |
| India West (Mumbai) | `bom` | `bom.ocir.io` |

## Your Configuration

Based on your repository path `ax1cmfkxkbut/ranga-tech/dev/app-1`:
- **Namespace**: `ax1cmfkxkbut`
- **Region**: `iad` (Ashburn) - **Default, change if different**
- **Registry**: `iad.ocir.io`

## How to Find Your Region

1. Log in to OCI Console
2. Look at the top navigation bar
3. You'll see region selector (e.g., "US East (Ashburn)")
4. Use the corresponding region code from the table above

## Full Image Paths

Once you confirm your region, your images will be at:
- Backend: `<region>.ocir.io/ax1cmfkxkbut/ranga-tech/dev/app-1:latest`
- Frontend: `<region>.ocir.io/ax1cmfkxkbut/ranga-tech/dev/app-2:latest`

Example with Ashburn region:
- Backend: `iad.ocir.io/ax1cmfkxkbut/ranga-tech/dev/app-1:latest`
- Frontend: `iad.ocir.io/ax1cmfkxkbut/ranga-tech/dev/app-2:latest`

## Updating the Configuration

If your region is not Ashburn (`iad`), update these files:

### 1. GitHub Actions Workflow
File: `.github/workflows/docker-build-push.yml`
```yaml
env:
  REGION: iad  # Change this to your region code
  REGISTRY: iad.ocir.io  # Change this to <your-region>.ocir.io
```

### 2. Manual Push Script
File: `.github/scripts/manual-docker-push.sh`
```bash
REGION="iad"  # Change this to your region code
```

## Username Format

Your OCI username should be in format:
```
<namespace>/<username>
```

Examples:
- `ax1cmfkxkbut/oracleidentitycloudservice/user@example.com`
- `ax1cmfkxkbut/your-oci-username`
