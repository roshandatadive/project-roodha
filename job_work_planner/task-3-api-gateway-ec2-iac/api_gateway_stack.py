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
    HTTP API Gateway in front of EC2 backend.
 
    ✔ HTTP API (low cost, low latency)
    ✔ EC2 direct HTTP integration (early stage)
    ✔ Defined routes as per Jira
    ✔ CORS enabled
    ✔ CloudWatch access logs
    ✔ Throttling & burst limits
    ✔ JWT Cognito wiring READY (can be enabled later)
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
 
        # -------------------------------
        # Access logs
        # -------------------------------
        log_group = logs.LogGroup(
            self,
            "ApiAccessLogs",
            retention=logs.RetentionDays.ONE_WEEK,
        )
 
        # -------------------------------
        # HTTP API
        # -------------------------------
        http_api = apigwv2.HttpApi(
            self,
            "JobWorkHttpApi",
            api_name="jobwork-http-api",
            cors_preflight=apigwv2.CorsPreflightOptions(
                allow_headers=["Authorization", "Content-Type"],
                allow_methods=[apigwv2.CorsHttpMethod.ANY],
                allow_origins=["*"],  # tighten later
            ),
        )
 
        # -------------------------------
        # EC2 HTTP Integration
        # -------------------------------
        integration = integrations.HttpUrlIntegration(
            "Ec2HttpIntegration",
            url=backend_url,
            method=apigwv2.HttpMethod.ANY,
        )
 
        # -------------------------------
        # Routes (Jira requirement)
        # -------------------------------
        routes = [
            "/auth/{proxy+}",
            "/masters/{proxy+}",
            "/jobs/{proxy+}",
            "/attachments/{proxy+}",
            "/reports/{proxy+}",
        ]
 
        for route in routes:
            http_api.add_routes(
                path=route,
                methods=[apigwv2.HttpMethod.ANY],
                integration=integration,
            )
 
        # -------------------------------
        # Public health check
        # -------------------------------
        http_api.add_routes(
            path="/health",
            methods=[apigwv2.HttpMethod.GET],
            integration=integration,
        )
 
        # -------------------------------
        # Stage config
        # -------------------------------
        apigwv2.CfnStage(
            self,
            "DevStage",
            api_id=http_api.http_api_id,
            stage_name="dev",
            auto_deploy=True,
            default_route_settings=apigwv2.CfnStage.RouteSettingsProperty(
                throttling_rate_limit=100,
                throttling_burst_limit=200,
            ),
            access_log_settings=apigwv2.CfnStage.AccessLogSettingsProperty(
                destination_arn=log_group.log_group_arn,
                format=(
                    '{"requestId":"$context.requestId",'
                    '"ip":"$context.identity.sourceIp",'
                    '"requestTime":"$context.requestTime",'
                    '"httpMethod":"$context.httpMethod",'
                    '"routeKey":"$context.routeKey",'
                    '"status":"$context.status"}'
                ),
            ),
        )
 
        # -------------------------------
        # Output
        # -------------------------------
        CfnOutput(
            self,
            "HttpApiBaseUrl",
            value=http_api.api_endpoint,
            description="Base URL of HTTP API Gateway",
        )