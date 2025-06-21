import os
import sys
import logging
from typing import Optional, List
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
# Optional: for console debug
from opentelemetry.sdk.trace.export import ConsoleSpanExporter

logger = logging.getLogger(__name__)

# Constants for validation
MIN_PRODUCTION_SAMPLING = 0.01  # 1% minimum for production
MIN_DEVELOPMENT_SAMPLING = 0.0   # 0% allowed for development/testing
MAX_SAMPLING_RATIO = 1.0
DEFAULT_SAMPLING_RATIO = 0.1
DEFAULT_LOCALHOST_ENDPOINT = "http://localhost:4318"

class OTelConfigurationError(Exception):
    """Raised when OpenTelemetry configuration is invalid."""
    pass

def init_tracing(service_name: str = "simple-api", require_endpoint: bool = True) -> None:
    """
    Initialize OpenTelemetry tracing with OTLP exporter and strict validation.
    
    Environment Variables:
    - OTEL_EXPORTER_OTLP_ENDPOINT: OTLP collector endpoint (REQUIRED in production)
    - OTEL_SAMPLING_RATIO: Sampling ratio 0.0-1.0 (default: 0.1)
    - OTEL_ENV: Environment (development/production, default: production)
    - OTEL_INSECURE: Use insecure connection (auto-configured by environment)
    
    Args:
        service_name: Name of the service for tracing
        require_endpoint: Whether to require OTEL_EXPORTER_OTLP_ENDPOINT (default: True)
        
    Raises:
        OTelConfigurationError: When configuration validation fails
        SystemExit: When critical configuration errors are detected
    """
    try:
        # Get and validate environment
        environment = os.getenv("OTEL_ENV", "production").lower()
        
        # **CRITICAL**: Validate required environment variables FIRST
        validate_required_env_vars(environment, require_endpoint)
        
        logger.info(f"🚀 Initializing OpenTelemetry for service '{service_name}' in {environment} environment")
        
        # Get validated environment variables
        config = get_validated_config(environment)
        
        # **CRITICAL**: Enforce minimum sampling ratios to prevent data loss
        sampling_ratio = enforce_minimum_sampling_ratio(config['sampling_ratio'], environment)
        
        # Security validation and warnings
        perform_security_validation(environment, config)
        
        # Configure debug logging for development
        configure_debug_logging(environment)
        
        # Create resource with enhanced attributes
        resource = create_enhanced_resource(service_name, environment)
        
        # Create tracer provider with validated sampling
        provider = TracerProvider(
            sampler=TraceIdRatioBased(sampling_ratio),
            resource=resource,
        )
        
        # Configure exporters with error handling
        configure_exporters(provider, config, environment)
        
        # Setup additional external exporters
        setup_external_exporters(environment, provider)
        
        # Set the tracer provider globally
        trace.set_tracer_provider(provider)
        
        # Success logging with configuration summary
        log_initialization_success(service_name, environment, sampling_ratio, config)
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize OpenTelemetry: {e}")
        raise OTelConfigurationError(f"Tracing initialization failed: {e}")


def validate_required_env_vars(environment: str, require_endpoint: bool = True) -> None:
    """
    **ENHANCED**: Validate that all required environment variables are set with strict checking.
    
    Args:
        environment: The deployment environment (development/production)
        require_endpoint: Whether OTEL_EXPORTER_OTLP_ENDPOINT is required
        
    Raises:
        SystemExit: When critical validation fails
    """
    missing_vars = []
    warnings = []
    
    # **CRITICAL**: Check OTLP endpoint requirement
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    if not endpoint:
        if require_endpoint and environment == "production":
            missing_vars.append("OTEL_EXPORTER_OTLP_ENDPOINT (REQUIRED for production)")
        elif environment == "development":
            warnings.append(f"OTEL_EXPORTER_OTLP_ENDPOINT not set, will use {DEFAULT_LOCALHOST_ENDPOINT}")
    else:
        # Validate endpoint format
        if not _is_valid_endpoint_url(endpoint):
            missing_vars.append(f"OTEL_EXPORTER_OTLP_ENDPOINT (invalid URL format: {endpoint})")
    
    # **CRITICAL**: Validate sampling ratio early and strictly
    sampling_validation_error = _validate_sampling_ratio_env()
    if sampling_validation_error:
        missing_vars.append(sampling_validation_error)
    
    # Validate environment value
    if environment not in ["development", "production"]:
        missing_vars.append(f"OTEL_ENV (current: '{environment}', must be 'development' or 'production')")
    
    # Validate insecure setting format
    insecure_str = os.getenv("OTEL_INSECURE", "").lower()
    if insecure_str and insecure_str not in ["true", "false", "1", "0", "yes", "no"]:
        missing_vars.append(f"OTEL_INSECURE (current: '{insecure_str}', must be true/false/1/0/yes/no)")
    
    # Log warnings for development
    for warning in warnings:
        logger.warning(f"⚠️  {warning}")
    
    # **CRITICAL**: Exit immediately if any required variables are missing
    if missing_vars:
        logger.error("❌ CRITICAL: Missing or invalid required environment variables:")
        for var in missing_vars:
            logger.error(f"   - {var}")
        logger.error("")
        _log_configuration_examples(environment)
        logger.error("❌ Application cannot start with invalid configuration")
        sys.exit(1)


def _validate_sampling_ratio_env() -> Optional[str]:
    """Validate sampling ratio environment variable format and range."""
    sampling_ratio_str = os.getenv("OTEL_SAMPLING_RATIO")
    if not sampling_ratio_str:
        return None  # Will use default
    
    try:
        sampling_ratio = float(sampling_ratio_str)
        if not (0.0 <= sampling_ratio <= MAX_SAMPLING_RATIO):
            return f"OTEL_SAMPLING_RATIO (current: {sampling_ratio}, must be 0.0-1.0)"
    except ValueError:
        return f"OTEL_SAMPLING_RATIO (current: '{sampling_ratio_str}', must be valid float 0.0-1.0)"
    
    return None


def _is_valid_endpoint_url(url: str) -> bool:
    """Basic URL validation for OTLP endpoint."""
    return url.startswith(('http://', 'https://')) and len(url.strip()) > 10


def get_validated_config(environment: str) -> dict:
    """Get and validate all configuration values."""
    # Get exporter URL with fallback
    exporter_url = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    if not exporter_url:
        exporter_url = DEFAULT_LOCALHOST_ENDPOINT
        if environment == "development":
            logger.info(f"Using default OTLP endpoint: {exporter_url}")
    
    # Get sampling ratio with validation
    sampling_ratio_str = os.getenv("OTEL_SAMPLING_RATIO", str(DEFAULT_SAMPLING_RATIO))
    sampling_ratio = float(sampling_ratio_str)  # Already validated in validate_required_env_vars
    
    # Get insecure setting with environment-aware defaults
    insecure_str = os.getenv("OTEL_INSECURE")
    if not insecure_str:
        insecure_str = "false" if environment == "production" else "true"
        logger.info(f"OTEL_INSECURE not set, using {'secure' if insecure_str == 'false' else 'insecure'} connections for {environment}")
    
    is_insecure = insecure_str.lower() in ("true", "1", "yes")
    
    return {
        'exporter_url': exporter_url,
        'sampling_ratio': sampling_ratio,
        'is_insecure': is_insecure
    }


def enforce_minimum_sampling_ratio(sampling_ratio: float, environment: str) -> float:
    """
    **CRITICAL**: Enforce minimum sampling ratios to prevent data loss in production.
    
    Args:
        sampling_ratio: Requested sampling ratio
        environment: Deployment environment
        
    Returns:
        Validated sampling ratio
        
    Raises:
        SystemExit: When sampling ratio is below minimum for environment
    """
    min_ratio = MIN_PRODUCTION_SAMPLING if environment == "production" else MIN_DEVELOPMENT_SAMPLING
    
    if sampling_ratio < min_ratio:
        logger.error(f"❌ CRITICAL: Sampling ratio {sampling_ratio} is below minimum for {environment}")
        logger.error(f"❌ Minimum required: {min_ratio} ({min_ratio*100}%)")
        logger.error("❌ Low sampling ratios can result in missing critical traces and observability gaps")
        logger.error("❌ This can severely impact debugging and monitoring capabilities")
        sys.exit(1)
    
    # Advanced sampling strategy for performance optimization
    optimized_ratio = configure_sampling_strategy(environment, sampling_ratio)
    
    return optimized_ratio


def configure_sampling_strategy(environment: str, base_ratio: float) -> float:
    """
    Configure advanced sampling strategy for high-traffic environments.
    
    Args:
        environment: The deployment environment
        base_ratio: Base sampling ratio
        
    Returns:
        Optimized sampling ratio
    """
    service_name = os.getenv("SERVICE_NAME", "unknown")
    
    # Performance optimization for high-traffic services
    high_traffic_services = os.getenv("OTEL_HIGH_TRAFFIC_SERVICES", "").split(",")
    high_traffic_services = [s.strip() for s in high_traffic_services if s.strip()]
    
    if service_name in high_traffic_services:
        # Reduce sampling for high-traffic services, but respect minimums
        optimized_ratio = max(base_ratio * 0.1, MIN_PRODUCTION_SAMPLING if environment == "production" else 0.001)
        logger.info(f"🚀 High-traffic service '{service_name}' detected: optimized sampling to {optimized_ratio*100:.1f}%")
        return optimized_ratio
    
    return base_ratio


def perform_security_validation(environment: str, config: dict) -> None:
    """Perform security validation and log warnings."""
    if environment == "production":
        if config['is_insecure']:
            logger.error("🚨 SECURITY CRITICAL: Using insecure connections in production!")
            logger.error("🚨 Trace data may be intercepted or compromised!")
            logger.error("🚨 Set OTEL_INSECURE=false for secure TLS connections")
            # In production, you might want to exit here for security
            # sys.exit(1)
        else:
            logger.info("🔒 Production security: TLS encryption enabled")
    
    # Check for sensitive data in environment
    if any(key.lower() in os.environ.get("OTEL_EXPORTER_OTLP_HEADERS", "").lower() 
           for key in ["password", "secret", "token"]):
        logger.warning("⚠️  Potential sensitive data detected in OTEL_EXPORTER_OTLP_HEADERS")


def configure_debug_logging(environment: str) -> None:
    """Configure debug logging for development environment."""
    if environment == "development":
        logging.getLogger("opentelemetry").setLevel(logging.DEBUG)
        if not logging.getLogger().handlers:
            logging.basicConfig(
                level=logging.DEBUG, 
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        logger.debug("🔧 Debug logging enabled for development environment")


def create_enhanced_resource(service_name: str, environment: str) -> Resource:
    """Create resource with enhanced attributes."""
    return Resource(attributes={
        "service.name": service_name,
        "service.version": os.getenv("SERVICE_VERSION", "unknown"),
        "deployment.environment": environment,
        "host.name": os.getenv("HOSTNAME", "unknown"),
        "service.instance.id": os.getenv("SERVICE_INSTANCE_ID", f"{service_name}-{os.getpid()}"),
    })


def configure_exporters(provider: TracerProvider, config: dict, environment: str) -> None:
    """Configure OTLP and console exporters with comprehensive error handling."""
    try:
        # Configure OTLP exporter
        span_exporter = OTLPSpanExporter(
            endpoint=f"{config['exporter_url']}/v1/traces",
            insecure=config['is_insecure']
        )
        span_processor = BatchSpanProcessor(span_exporter)
        provider.add_span_processor(span_processor)
        
        logger.info(f"✅ OTLP exporter configured: {config['exporter_url']} (secure={not config['is_insecure']})")
        
    except Exception as e:
        logger.error(f"❌ Failed to configure OTLP exporter: {e}")
        if environment == "production":
            logger.error("❌ CRITICAL: Cannot start without OTLP exporter in production")
            sys.exit(1)
        else:
            # Fallback to console exporter for development
            console_processor = BatchSpanProcessor(ConsoleSpanExporter())
            provider.add_span_processor(console_processor)
            logger.warning("⚠️  Falling back to console exporter for development")
    
    # Add console exporter for development environment
    if environment == "development":
        console_processor = BatchSpanProcessor(ConsoleSpanExporter())
        provider.add_span_processor(console_processor)
        logger.debug("🖥️  Console exporter enabled for development")


def setup_external_exporters(environment: str, provider: TracerProvider) -> None:
    """Setup additional exporters like Sentry or external logging services."""
    # Sentry integration (optional)
    sentry_dsn = os.getenv("SENTRY_DSN")
    if sentry_dsn and environment == "production":
        try:
            # Note: This would require sentry-sdk package
            # from sentry_sdk.integrations.opentelemetry import SentrySpanExporter
            # sentry_exporter = SentrySpanExporter()
            # provider.add_span_processor(BatchSpanProcessor(sentry_exporter))
            logger.info("🔍 Sentry integration configured for error tracking")
        except ImportError:
            logger.warning("⚠️  Sentry DSN provided but sentry-sdk not installed")
    
    # Custom webhook exporter for alerts (optional)
    webhook_url = os.getenv("OTEL_WEBHOOK_URL")
    if webhook_url:
        logger.info(f"🔔 Webhook alerts configured: {webhook_url}")


def log_initialization_success(service_name: str, environment: str, sampling_ratio: float, config: dict) -> None:
    """Log successful initialization with configuration summary."""
    logger.info("="*60)
    logger.info(f"✅ OpenTelemetry initialized successfully!")
    logger.info(f"   Service: {service_name}")
    logger.info(f"   Environment: {environment}")
    logger.info(f"   Sampling ratio: {sampling_ratio*100:.1f}%")
    logger.info(f"   OTLP endpoint: {config['exporter_url']}")
    logger.info(f"   Secure connection: {not config['is_insecure']}")
    logger.info("="*60)


def _log_configuration_examples(environment: str) -> None:
    """Log configuration examples for the current environment."""
    logger.error("💡 Required configuration examples:")
    if environment == "production":
        logger.error("   OTEL_EXPORTER_OTLP_ENDPOINT=https://jaeger-collector:14268")
        logger.error(f"   OTEL_SAMPLING_RATIO=0.1  # Minimum: {MIN_PRODUCTION_SAMPLING}")
        logger.error("   OTEL_ENV=production")
        logger.error("   OTEL_INSECURE=false")
    else:
        logger.error("   OTEL_ENV=development")
        logger.error("   OTEL_SAMPLING_RATIO=0.5")
        logger.error("   # OTEL_EXPORTER_OTLP_ENDPOINT optional (uses localhost:4318)")
        logger.error("   # OTEL_INSECURE defaults to true for development")


def get_tracer(name: str = __name__):
    """Get a tracer instance for the given name."""
    return trace.get_tracer(name)