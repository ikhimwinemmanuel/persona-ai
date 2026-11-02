
param(
    [ValidateSet("dev", "test", "prod")]
    [string]$Environment = "dev",

    [string]$ProjectName = "personaai"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path $PSScriptRoot -Parent

Write-Host "Deploying $ProjectName to $Environment..." -ForegroundColor Cyan

# 1. Build the Lambda deployment package
Set-Location (Join-Path $ProjectRoot "backend")

Write-Host "Building Lambda package..." -ForegroundColor Yellow
uv run deploy.py

if ($LASTEXITCODE -ne 0) {
    throw "Lambda package build failed."
}

# 2. Initialise Terraform and select the environment
Set-Location (Join-Path $ProjectRoot "terraform")

terraform init -input=false

if ($LASTEXITCODE -ne 0) {
    throw "Terraform initialisation failed."
}

# Get existing workspace names without Terraform formatting
$workspaces = terraform workspace list |
    ForEach-Object { ($_ -replace '^\s*\*?\s*', '').Trim() }

if ($Environment -notin $workspaces) {
    terraform workspace new $Environment
} else {
    terraform workspace select $Environment
}

if ($LASTEXITCODE -ne 0) {
    throw "Terraform workspace selection failed."
}

# 3. Plan and apply infrastructure changes
terraform plan `
    -var="project_name=$ProjectName" `
    -var="environment=$Environment" `
    -out="deployment.tfplan"

if ($LASTEXITCODE -ne 0) {
    throw "Terraform plan failed."
}

Write-Host "Review the Terraform plan before applying." -ForegroundColor Yellow

terraform apply "deployment.tfplan"

if ($LASTEXITCODE -ne 0) {
    throw "Terraform deployment failed."
}

# 4. Retrieve infrastructure outputs
$ApiUrl = terraform output -raw api_gateway_url
$FrontendBucket = terraform output -raw s3_frontend_bucket
$CloudFrontUrl = terraform output -raw cloudfront_url

# 5. Build and upload the frontend
Set-Location (Join-Path $ProjectRoot "frontend")

$env:NEXT_PUBLIC_API_URL = $ApiUrl

npm install

if ($LASTEXITCODE -ne 0) {
    throw "Frontend dependency installation failed."
}

npm run build

if ($LASTEXITCODE -ne 0) {
    throw "Frontend build failed."
}

aws s3 sync ".\out" "s3://$FrontendBucket/" --delete

if ($LASTEXITCODE -ne 0) {
    throw "Frontend upload failed."
}

Write-Host "Deployment complete!" -ForegroundColor Green
Write-Host "Frontend: $CloudFrontUrl"
Write-Host "API: $ApiUrl"
