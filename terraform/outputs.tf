# API Gateway endpoint
output "api_gateway_url" {
  description = "URL of the PersonaAI API Gateway"
  value       = aws_apigatewayv2_api.main.api_endpoint
}

# CloudFront frontend URL
output "cloudfront_url" {
  description = "URL of the PersonaAI frontend"
  value       = "https://${aws_cloudfront_distribution.main.domain_name}"
}

# Frontend S3 bucket
output "s3_frontend_bucket" {
  description = "S3 bucket hosting the frontend"
  value       = aws_s3_bucket.frontend.id
}

# Conversation memory S3 bucket
output "s3_memory_bucket" {
  description = "S3 bucket storing conversation history"
  value       = aws_s3_bucket.memory.id
}

# Lambda function name
output "lambda_function_name" {
  description = "Name of the PersonaAI Lambda function"
  value       = aws_lambda_function.api.function_name
}