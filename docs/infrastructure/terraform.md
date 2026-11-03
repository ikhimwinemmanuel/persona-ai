# PersonaAI — Infrastructure as Code

## Overview

PersonaAI uses Terraform to provision a serverless AWS environment for a full-stack AI assistant built with Next.js, FastAPI, and Amazon Bedrock.

The infrastructure is configured in the AWS Sydney region (`ap-southeast-2`). A separate development environment was provisioned and validated without modifying the original manually deployed application.

## Architecture

| Component | Service | Responsibility |
|---|---|---|
| Frontend | Next.js, Amazon S3, CloudFront | Static website hosting and content delivery |
| API | Amazon API Gateway HTTP API | Public HTTPS endpoints and request throttling |
| Backend | AWS Lambda, FastAPI, Mangum | Application logic and API request handling |
| AI inference | Amazon Bedrock, Nova 2 Lite | AI-generated responses |
| Conversation memory | Amazon S3 | Persistent session history |
| Access control | AWS IAM | Deployment and runtime permissions |
| Infrastructure | Terraform | AWS resource provisioning and state management |

The browser retrieves the static frontend through CloudFront and sends chat requests directly to API Gateway. The Lambda backend invokes Amazon Bedrock and accesses a separate S3 bucket for conversation history.

## Terraform Configuration

The `terraform/` directory contains:

- `versions.tf` — Terraform and provider requirements.
- `variables.tf` — Project, environment, model, and deployment settings.
- `main.tf` — AWS resource definitions, IAM policies, and service integrations.
- `outputs.tf` — API URL, CloudFront URL, Lambda name, and S3 bucket names.

Terraform workspaces provide separate state environments. The verified deployment uses the `dev` workspace and the `personaai-dev` resource naming convention.

Terraform state and local variable files are excluded from version control.

## Deployment

Prerequisites include Terraform, AWS CLI credentials with suitable permissions, Python and `uv`, Docker, Node.js, and npm.

The PowerShell deployment script is located at `scripts/deploy.ps1`. It performs the following operations:

1. Builds the Lambda deployment package.
2. Initialises Terraform and selects the appropriate workspace.
3. Generates and applies a Terraform execution plan.
4. Retrieves deployed infrastructure outputs.
5. Builds the Next.js frontend using the environment-specific API URL.
6. Uploads the static frontend to S3.

To deploy the development environment from the repository root:

```powershell
.\scripts\deploy.ps1 -Environment dev
```

The script automatically applies its generated Terraform plan. Review the target environment and planned changes before using it.

## Validation

The development deployment was verified through:

- A successful API health check.
- An Amazon Bedrock Nova 2 Lite chat response.
- Conversation memory retrieval using an existing session ID.
- A successful Next.js production build.
- A successful frontend upload to S3.
- A working browser-based chat interface served through CloudFront.
- Terraform state inspection confirming 20 managed AWS resources.
- A final `terraform plan` reporting no changes.

Development deployment: https://d2p51fync7zgnd.cloudfront.net

## Deployment Challenges

### API Gateway IAM permissions

Initial provisioning was interrupted by IAM `AccessDeniedException` errors involving API Gateway creation and stage tagging.

The deployment permissions were updated, and Terraform plans were regenerated after each failed operation. Successfully provisioned resources remained recorded in Terraform state, allowing deployment to continue without recreating them.

### Environment separation

The original application was already deployed manually. A distinct Terraform-managed development stack was introduced to avoid disrupting that deployment.

### Frontend API configuration

The Next.js application uses `NEXT_PUBLIC_API_URL` to select the API endpoint at build time. The development frontend was built using the newly provisioned API Gateway URL before being uploaded to S3.

## Cost Management

Infracost was used to evaluate the Terraform configuration. Its baseline estimate excluded usage-dependent charges and Amazon Bedrock inference.

CloudFront was configured with `PriceClass_200`, and API Gateway throttling was configured with a rate limit of five requests per second and burst limit of ten.

Actual AWS charges depend on traffic, storage, inference usage, and other service consumption.