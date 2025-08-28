#!/bin/bash

# AI Camera Version Management Script
# Usage: ./scripts/version.sh [major|minor|patch|alpha|beta|rc] [message]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

# Function to get current version
get_current_version() {
    local version_file="package.json"
    if [ -f "$version_file" ]; then
        grep '"version"' "$version_file" | sed 's/.*"version": "\(.*\)".*/\1/'
    else
        print_error "Version file not found: $version_file"
        exit 1
    fi
}

# Function to update version in package.json
update_version() {
    local new_version=$1
    local version_file="package.json"
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/\"version\": \"[^\"]*\"/\"version\": \"$new_version\"/" "$version_file"
    else
        # Linux
        sed -i "s/\"version\": \"[^\"]*\"/\"version\": \"$new_version\"/" "$version_file"
    fi
    
    print_status "Updated $version_file to version $new_version"
}

# Function to update server version
update_server_version() {
    local new_version=$1
    local version_file="server/package.json"
    
    if [ -f "$version_file" ]; then
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            sed -i '' "s/\"version\": \"[^\"]*\"/\"version\": \"$new_version\"/" "$version_file"
        else
            # Linux
            sed -i "s/\"version\": \"[^\"]*\"/\"version\": \"$new_version\"/" "$version_file"
        fi
        
        print_status "Updated $version_file to version $new_version"
    fi
}

# Function to update edge version
update_edge_version() {
    local new_version=$1
    local version_file="edge/src/__init__.py"
    
    if [ -f "$version_file" ]; then
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            sed -i '' "s/__version__ = \"[^\"]*\"/__version__ = \"$new_version\"/" "$version_file"
        else
            # Linux
            sed -i "s/__version__ = \"[^\"]*\"/__version__ = \"$new_version\"/" "$version_file"
        fi
        
        print_status "Updated $version_file to version $new_version"
    else
        # Create version file if it doesn't exist
        echo "__version__ = \"$new_version\"" > "$version_file"
        print_status "Created $version_file with version $new_version"
    fi
}

# Function to increment version
increment_version() {
    local current_version=$1
    local increment_type=$2
    
    IFS='.' read -ra VERSION_PARTS <<< "$current_version"
    local major=${VERSION_PARTS[0]}
    local minor=${VERSION_PARTS[1]}
    local patch=${VERSION_PARTS[2]}
    
    case $increment_type in
        "major")
            major=$((major + 1))
            minor=0
            patch=0
            ;;
        "minor")
            minor=$((minor + 1))
            patch=0
            ;;
        "patch")
            patch=$((patch + 1))
            ;;
        *)
            print_error "Invalid increment type: $increment_type"
            exit 1
            ;;
    esac
    
    echo "$major.$minor.$patch"
}

# Function to create pre-release version
create_prerelease() {
    local base_version=$1
    local prerelease_type=$2
    local prerelease_number=1
    
    # Check if prerelease already exists
    if git tag | grep -q "^v$base_version-$prerelease_type\."; then
        prerelease_number=$(git tag | grep "^v$base_version-$prerelease_type\." | tail -1 | sed "s/v$base_version-$prerelease_type\.//")
        prerelease_number=$((prerelease_number + 1))
    fi
    
    echo "$base_version-$prerelease_type.$prerelease_number"
}

# Function to create git tag
create_git_tag() {
    local version=$1
    local message=$2
    
    if [ -z "$message" ]; then
        message="Release version $version"
    fi
    
    git add .
    git commit -m "chore: bump version to $version"
    git tag -a "v$version" -m "$message"
    
    print_status "Created git tag v$version"
}

# Function to push changes
push_changes() {
    local version=$1
    
    git push origin main
    git push origin "v$version"
    
    print_status "Pushed changes and tag v$version to remote"
}

# Function to show help
show_help() {
    echo "AI Camera Version Management Script"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  major              Increment major version (X.0.0)"
    echo "  minor              Increment minor version (X.Y.0)"
    echo "  patch              Increment patch version (X.Y.Z)"
    echo "  alpha              Create alpha prerelease"
    echo "  beta               Create beta prerelease"
    echo "  rc                 Create release candidate"
    echo "  show               Show current version"
    echo "  help               Show this help message"
    echo ""
    echo "Options:"
    echo "  -m, --message      Commit message for the version bump"
    echo "  -p, --push         Push changes to remote repository"
    echo ""
    echo "Examples:"
    echo "  $0 patch                    # Bump patch version"
    echo "  $0 minor -m 'New features'  # Bump minor version with message"
    echo "  $0 alpha -p                 # Create alpha prerelease and push"
}

# Main script logic
main() {
    print_header "AI Camera Version Management"
    
    # Check if we're in a git repository
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        print_error "Not in a git repository"
        exit 1
    fi
    
    # Check if working directory is clean
    if ! git diff-index --quiet HEAD --; then
        print_warning "Working directory is not clean. Please commit or stash changes first."
        exit 1
    fi
    
    local command=$1
    local message=""
    local push_changes=false
    
    # Parse arguments
    shift
    while [[ $# -gt 0 ]]; do
        case $1 in
            -m|--message)
                message="$2"
                shift 2
                ;;
            -p|--push)
                push_changes=true
                shift
                ;;
            *)
                print_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    case $command in
        "show")
            local current_version=$(get_current_version)
            print_status "Current version: $current_version"
            ;;
        "major"|"minor"|"patch")
            local current_version=$(get_current_version)
            local new_version=$(increment_version "$current_version" "$command")
            
            print_status "Bumping $command version from $current_version to $new_version"
            
            update_version "$new_version"
            update_server_version "$new_version"
            update_edge_version "$new_version"
            
            create_git_tag "$new_version" "$message"
            
            if [ "$push_changes" = true ]; then
                push_changes "$new_version"
            fi
            
            print_status "Version bumped to $new_version"
            ;;
        "alpha"|"beta"|"rc")
            local current_version=$(get_current_version)
            local prerelease_version=$(create_prerelease "$current_version" "$command")
            
            print_status "Creating $command prerelease: $prerelease_version"
            
            update_version "$prerelease_version"
            update_server_version "$prerelease_version"
            update_edge_version "$prerelease_version"
            
            create_git_tag "$prerelease_version" "$message"
            
            if [ "$push_changes" = true ]; then
                push_changes "$prerelease_version"
            fi
            
            print_status "Created $command prerelease: $prerelease_version"
            ;;
        "help"|"--help"|"-h")
            show_help
            ;;
        "")
            print_error "No command specified"
            show_help
            exit 1
            ;;
        *)
            print_error "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
