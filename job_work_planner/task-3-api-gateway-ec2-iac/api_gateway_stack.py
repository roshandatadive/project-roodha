# api_gateway_stack.py
#
# Purpose:
# This stack provisions an AWS API Gateway HTTP API that acts as the
# single public entry point for backend services running on EC2.
#
# Design principles:
# - Low cost & low latency (HTTP API, not REST API)
# - Stateless and decoupled from compute
# - Backend-agnostic (EC2 now, ALB later)
# - Production-safe defaults with clear extension points
#
# This implementation is intentionally explicit and readable,
# suitable for real SaaS infrastructure.
 
from aws_cdk import (
    Stack,
    CfnOutput,
    aws_apigatewayv2 as apigwv2,
    aws_apigatewayv2_integrations as integrations,
    aws_logs as logs,
)
from constructs import Construct
 
 
class ApiGatewayStack(Stack):
    """
    ApiGatewayStack
 
    Responsibilities:
    - Create an HTTP API Gateway
    - Route external traffic to an EC2-hosted backend
    - Define SaaS-style route structure
    - Enable CORS and access logging
    - Prepare the system for future auth (Cognito) and ALB integration
    """
 
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        backend_url: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
 
        # ---------------------------------------------------------------------
        # CloudWatch Log Group
        #
        # Why:
        # - Required for operational visibility
        # - Enables request tracing and debugging
        # - Keeps logs scoped to the API lifecycle
        # ---------------------------------------------------------------------
        access_log_group = logs.LogGroup(
            self,
            "ApiGatewayAccessLogs",
            retention=logs.RetentionDays.ONE_WEEK,  # cost-conscious default
        )
 
        # ---------------------------------------------------------------------
        # HTTP API Gateway
        #
        # Why HTTP API:
        # - Significantly cheaper than REST API
        # - Lower latency
        # - Perfect fit for proxying backend services
        # ---------------------------------------------------------------------
        http_api = apigwv2.HttpApi(
            self,
            "JobWorkHttpApi",
            api_name="jobwork-http-api",
            cors_preflight=apigwv2.CorsPreflightOptions(
                allow_headers=[
                    "Authorization",
                    "Content-Type",
                ],
                allow_methods=[
                    apigwv2.CorsHttpMethod.GET,
                    apigwv2.CorsHttpMethod.POST,
                    apigwv2.CorsHttpMethod.PUT,
                    apigwv2.CorsHttpMethod.DELETE,
                    apigwv2.CorsHttpMethod.OPTIONS,
                ],
                # Open for dev; restrict to frontend domain in prod
                allow_origins=["*"],
            ),
        )
 
        # ---------------------------------------------------------------------
        # Backend Integration
        #
        # Current state:
        # - Direct integration to EC2 public endpoint
        #
        # Future state (no code rewrite needed):
        # - Replace backend_url with ALB DNS name
        # ---------------------------------------------------------------------
        backend_integration = integrations.HttpUrlIntegration(
            "Ec2BackendIntegration",
            url=backend_url,
        )
 
        # ---------------------------------------------------------------------
        # Route Definitions (as per Jira)
        #
        # {proxy+} allows the backend application
        # to own routing logic internally.
        # ---------------------------------------------------------------------
        api_routes = [
            "/auth/{proxy+}",
            "/masters/{proxy+}",
            "/jobs/{proxy+}",
            "/attachments/{proxy+}",
            "/reports/{proxy+}",
        ]
 
        for route in api_routes:
            http_api.add_routes(
                path=route,
                methods=[apigwv2.HttpMethod.ANY],
                integration=backend_integration,
            )
 
        # ---------------------------------------------------------------------
        # Stage Configuration
        #
        # Why explicit stage:
        # - Enables environment separation (dev / prod)
        # - Required for access logging
        # - Supports future throttling & WAF
        #
        # NOTE:
        # AccessLogSettings must be defined via CfnStage
        # (L1 construct) — this is the correct CDK v2 approach.
        # ---------------------------------------------------------------------
        apigwv2.CfnStage(
            self,
            "DevStage",
            api_id=http_api.http_api_id,
            stage_name="dev",
            auto_deploy=True,
            access_log_settings=apigwv2.CfnStage.AccessLogSettingsProperty(
                destination_arn=access_log_group.log_group_arn,
                format=(
                    '{"requestId":"$context.requestId",'
                    '"ip":"$context.identity.sourceIp",'
                    '"requestTime":"$context.requestTime",'
                    '"httpMethod":"$context.httpMethod",'
                    '"routeKey":"$context.routeKey",'
                    '"status":"$context.status",'
                    '"protocol":"$context.protocol",'
                    '"responseLength":"$context.responseLength"}'
                ),
            ),
        )
 
        # ---------------------------------------------------------------------
        # Outputs
        #
        # Exposed for:
        # - Testing
        # - Frontend integration
        # - Documentation and handover
        # ---------------------------------------------------------------------
        CfnOutput(
            self,
            "HttpApiBaseUrl",
            value=http_api.api_endpoint,
            description="Base URL of the JobWork HTTP API Gateway",
        )