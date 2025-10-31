# Home Assistant Add-ons Development Guide

This repository contains Home Assistant add-ons. Here's what you need to know to work effectively with this codebase.

## Project Architecture

### Add-on Structure
- Each add-on lives in its own directory and follows this structure:
  ```
  addon-name/
    ├── Dockerfile           # Container definition
    ├── build.json          # Build configuration and base images
    ├── config.json         # Add-on configuration and metadata
    ├── README.md           # Add-on documentation
    └── rootfs/             # File system overlay
        ├── etc/
        │   └── services.d/ # Service definitions
        └── usr/
            └── bin/        # Application binaries
  ```

### Key Components
1. **Add-on Configuration** (`config.json`):
   - Defines add-on metadata, options schema, and permissions
   - Example from `s3-backup`: `options` define user-configurable settings, `schema` validates them

2. **Service Management**:
   - Services are managed through `/etc/services.d/` scripts
   - Each service has `run` and `finish` scripts
   - Example: `s3-backup/rootfs/etc/services.d/amazon-s3-backup/`

3. **Container Configuration** (`build.json`):
   - Specifies base images for different architectures
   - Supports: aarch64, amd64, armhf, armv7, i386

## Development Patterns

### Python Add-on Development
Key patterns from `s3-backup`:

1. **Configuration Management**:
   ```python
   # Use Config class pattern with validation
   class Config:
       def __init__(self):
           self.validate()  # Always validate configuration
   ```

2. **Error Handling**:
   ```python
   # Custom exceptions for each component
   class ConfigError(Exception): pass
   class S3BucketError(Exception): pass
   class SupervisorAPIError(Exception): pass
   ```

3. **API Integration**:
   - Use REST client classes (see `SupervisorAPI`)
   - Always handle connection and timeout errors
   - Include authentication (`_BearerAuth`)

### Home Assistant Integration
1. **Supervisor API**:
   - Base URL: `http://supervisor`
   - Bearer token authentication required
   - Handle API responses carefully, especially JSON parsing

2. **Add-on Options**:
   - Define in `config.json` schema
   - Access via environment variables in code
   - Always validate before use

## Common Tasks

### Building Add-ons
```bash
# Build for specific architecture
docker build \
  --build-arg BUILD_FROM="hassioaddons/base-amd64:7.2.0" \
  --build-arg BUILD_ARCH="amd64" \
  .
```

### Testing
1. Build the add-on
2. Configure test options in Home Assistant
3. Verify logs for proper initialization
4. Test error handling with invalid configurations

## Best Practices

1. **Logging**:
   - Use consistent logging levels
   - Include context in log messages
   - Support configurable log levels

2. **Configuration**:
   - Provide clear schema validation
   - Use sensible defaults
   - Document all options

3. **Error Handling**:
   - Use component-specific exceptions
   - Log errors with context
   - Fail gracefully when possible

4. **Docker**:
   - Use multi-arch base images
   - Follow Home Assistant add-on guidelines
   - Include proper labels and metadata