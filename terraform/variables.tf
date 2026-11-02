variable "project_name" {
  description = "Name prefix for AWS resources"
  type        = string
}

variable "environment" {
  description = "Deployment environment"
  type        = string

  validation {
    condition     = contains(["dev", "test", "prod"], var.environment)
    error_message = "Environment must be dev, test, or prod."
  }
}

variable "bedrock_model_id" {
  description = "Amazon Bedrock model ID"
  type        = string
  default     = "global.amazon.nova-2-lite-v1:0"
}

variable "lambda_timeout" {
  description = "Lambda function timeout in seconds"
  type        = number
  default     = 60
}

variable "api_throttle_burst_limit" {
  description = "Maximum burst of API requests"
  type        = number
  default     = 10
}

variable "api_throttle_rate_limit" {
  description = "Maximum sustained API requests per second"
  type        = number
  default     = 5
}

variable "use_custom_domain" {
  description = "Whether to use a custom domain"
  type        = bool
  default     = false
}

variable "root_domain" {
  description = "Custom domain name"
  type        = string
  default     = ""
}