#!/bin/bash
# MCP Tools Build Script with Semantic Versioning
set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $*" >&2
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $*" >&2
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $*" >&2
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*" >&2
}

# Get current version
get_current_version() {
    if [[ -f "version.py" ]]; then
        python3 version.py current 2>/dev/null | sed -n 's/Current version: //p' | head -1 | tr -d ' \n' || echo "2.0.0"
    else
        echo "2.0.0"
    fi
}

# Get container runtime
get_container_runtime() {
    if command -v podman >/dev/null 2>&1; then
        echo "podman"
    elif command -v docker >/dev/null 2>&1; then
        echo "docker"
    else
        log_error "Neither podman nor docker found. Please install one of them."
        exit 1
    fi
}

# Build container with version tags
build_container() {
    local version="$1"
    local container_runtime="$2"
    local image_name="mcp-tools"
    
    log_info "Building $image_name:$version using $container_runtime..."
    
    # Build with version tag
    if $container_runtime build -t "$image_name:$version" .; then
        log_success "Built $image_name:$version"
    else
        log_error "Failed to build $image_name:$version"
        return 1
    fi
    
    # Tag as latest for compatibility
    if $container_runtime tag "$image_name:$version" "$image_name:latest"; then
        log_success "Tagged $image_name:latest"
    else
        log_warn "Failed to tag as latest (non-critical)"
    fi
    
    # Show built images
    log_info "Available $image_name images:"
    $container_runtime images | grep "$image_name" || true
}

# Push to registry (optional)
push_container() {
    local version="$1"
    local container_runtime="$2"
    local registry="${3:-}"
    local image_name="mcp-tools"
    
    if [[ -z "$registry" ]]; then
        log_warn "No registry specified, skipping push"
        return 0
    fi
    
    local full_image="$registry/$image_name"
    
    # Tag for registry
    $container_runtime tag "$image_name:$version" "$full_image:$version"
    $container_runtime tag "$image_name:latest" "$full_image:latest"
    
    # Push version tag
    if $container_runtime push "$full_image:$version"; then
        log_success "Pushed $full_image:$version"
    else
        log_error "Failed to push $full_image:$version"
        return 1
    fi
    
    # Push latest tag
    if $container_runtime push "$full_image:latest"; then
        log_success "Pushed $full_image:latest"
    else
        log_warn "Failed to push latest tag (non-critical)"
    fi
}

# Main build function
main() {
    local version_type=""
    local push_registry=""
    local show_help=false
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --version)
                version_type="$2"
                shift 2
                ;;
            --push)
                push_registry="$2"
                shift 2
                ;;
            --help|-h)
                show_help=true
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                show_help=true
                break
                ;;
        esac
    done
    
    if [[ "$show_help" == true ]]; then
        cat << EOF
MCP Tools Build Script with Semantic Versioning

Usage: $0 [OPTIONS]

Options:
  --version TYPE      Bump version before building (major|minor|patch)
  --push REGISTRY     Push to container registry after building
  --help, -h          Show this help message

Examples:
  $0                                    # Build with current version
  $0 --version patch                    # Bump patch version and build
  $0 --version minor --push registry.example.com  # Bump version, build, and push

Version Tags:
  - Builds container with semantic version tag (e.g., mcp-tools:2.1.0)
  - Also tags as 'latest' for compatibility
  - Supports both podman and docker (prefers podman)

Container Runtime:
  - Automatically detects podman or docker
  - Prefers podman if both are available
  - Uses OCI format for maximum compatibility
EOF
        exit 0
    fi
    
    log_info "MCP Tools Build Script v1.0"
    log_info "Working directory: $(pwd)"
    
    # Get container runtime
    local container_runtime
    container_runtime=$(get_container_runtime)
    log_info "Using container runtime: $container_runtime"
    
    # Handle version bumping
    local current_version
    if [[ -n "$version_type" ]]; then
        if [[ ! -f "version.py" ]]; then
            log_error "version.py not found. Cannot bump version."
            exit 1
        fi
        
        log_info "Bumping $version_type version..."
        if python3 version.py bump "$version_type"; then
            log_success "Version bumped successfully"
        else
            log_error "Version bump failed"
            exit 1
        fi
    fi
    
    # Get current version
    current_version=$(get_current_version)
    log_info "Building MCP Tools v$current_version"
    
    # Build container
    if build_container "$current_version" "$container_runtime"; then
        log_success "Container build completed successfully"
    else
        log_error "Container build failed"
        exit 1
    fi
    
    # Push to registry if requested
    if [[ -n "$push_registry" ]]; then
        if push_container "$current_version" "$container_runtime" "$push_registry"; then
            log_success "Container push completed successfully"
        else
            log_error "Container push failed"
            exit 1
        fi
    fi
    
    # Show final status
    echo ""
    log_success "🎉 Build completed successfully!"
    log_info "Version: $current_version"
    log_info "Image: mcp-tools:$current_version"
    log_info "Runtime: $container_runtime"
    
    if [[ -n "$push_registry" ]]; then
        log_info "Registry: $push_registry/mcp-tools:$current_version"
    fi
    
    echo ""
    log_info "To run the container:"
    echo "  $container_runtime run --rm -p 8002:8002 mcp-tools:$current_version"
    echo ""
    log_info "To run with latest tag:"
    echo "  $container_runtime run --rm -p 8002:8002 mcp-tools:latest"
}

main "$@"