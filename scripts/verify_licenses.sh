#!/bin/bash

# AI Camera v2.0 - License Checker Script
# This script analyzes Python dependencies and generates license compliance reports

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
VENV_PATH="edge/installation/venv_hailo"
REPORT_DIR="docs/edge/license-reports"
DATE=$(date +%Y%m%d_%H%M%S)

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if virtual environment exists
check_venv() {
    if [[ ! -d "$VENV_PATH" ]]; then
        print_error "Virtual environment not found at $VENV_PATH"
        print_status "Please run the installation script first"
        exit 1
    fi
}

# Function to activate virtual environment
activate_venv() {
    print_status "Activating virtual environment..."
    source "$VENV_PATH/bin/activate"
    print_success "Virtual environment activated"
}

# Function to install license checkers
install_checkers() {
    print_status "Installing license checking tools..."
    
    if ! pip show licensecheck >/dev/null 2>&1; then
        print_status "Installing licensecheck..."
        pip install licensecheck
    fi
    
    if ! pip show pip-licenses >/dev/null 2>&1; then
        print_status "Installing pip-licenses..."
        pip install pip-licenses
    fi
    
    print_success "License checking tools installed"
}

# Function to create report directory
create_report_dir() {
    if [[ ! -d "$REPORT_DIR" ]]; then
        mkdir -p "$REPORT_DIR"
        print_status "Created report directory: $REPORT_DIR"
    fi
}

# Function to generate license reports
generate_reports() {
    print_status "Generating license reports..."
    
    # Generate detailed report
    print_status "Creating detailed license report..."
    pip-licenses --format=markdown --output-file="$REPORT_DIR/python_licenses_$DATE.md"
    
    # Generate summary report
    print_status "Creating summary report..."
    pip-licenses --format=plain > "$REPORT_DIR/license_summary_$DATE.txt"
    
    # Generate JSON report for programmatic use
    print_status "Creating JSON report..."
    pip-licenses --format=json --output-file="$REPORT_DIR/license_data_$DATE.json"
    
    print_success "License reports generated in $REPORT_DIR"
}

# Function to analyze license compatibility
analyze_compatibility() {
    print_status "Analyzing license compatibility..."
    
    # Count licenses by type
    local mit_count=$(grep -c "MIT License" "$REPORT_DIR/license_summary_$DATE.txt" || echo "0")
    local bsd_count=$(grep -c "BSD License" "$REPORT_DIR/license_summary_$DATE.txt" || echo "0")
    local apache_count=$(grep -c "Apache" "$REPORT_DIR/license_summary_$DATE.txt" || echo "0")
    local gpl_count=$(grep -c "GPL" "$REPORT_DIR/license_summary_$DATE.txt" || echo "0")
    local unknown_count=$(grep -c "UNKNOWN" "$REPORT_DIR/license_summary_$DATE.txt" || echo "0")
    
    # Create compatibility report
    cat > "$REPORT_DIR/compatibility_report_$DATE.md" << EOF
# License Compatibility Report - $(date)

## Summary
- MIT License: $mit_count packages
- BSD License: $bsd_count packages  
- Apache License: $apache_count packages
- GPL License: $gpl_count packages
- UNKNOWN: $unknown_count packages

## Compatibility Assessment

### ✅ Compatible Licenses
- MIT License ($mit_count packages)
- BSD License ($bsd_count packages)
- Apache License 2.0 ($apache_count packages)

### ⚠️ Licenses Requiring Attention
- GPL Licenses ($gpl_count packages) - May require source disclosure
- UNKNOWN Licenses ($unknown_count packages) - Need investigation

### Overall Status
- Compatible packages: $((mit_count + bsd_count + apache_count))
- Total packages analyzed: $(wc -l < "$REPORT_DIR/license_summary_$DATE.txt")
- Compatibility rate: $(echo "scale=1; ($mit_count + $bsd_count + $apache_count) * 100 / $(wc -l < "$REPORT_DIR/license_summary_$DATE.txt")" | bc -l)%

## Recommendations
1. Investigate UNKNOWN license packages
2. Review GPL dependencies for compliance requirements
3. Update LICENSE_ATTRIBUTION.md with new findings
4. Monitor for license changes in updates

EOF
    
    print_success "Compatibility analysis complete"
}

# Function to check for license violations
check_violations() {
    print_status "Checking for potential license violations..."
    
    local violations=0
    
    # Check for incompatible licenses
    if grep -q "UNKNOWN" "$REPORT_DIR/license_summary_$DATE.txt"; then
        print_warning "Found packages with UNKNOWN licenses"
        violations=$((violations + 1))
    fi
    
    # Check for GPL licenses
    if grep -q "GPL" "$REPORT_DIR/license_summary_$DATE.txt"; then
        print_warning "Found GPL-licensed packages - review compliance requirements"
        violations=$((violations + 1))
    fi
    
    if [[ $violations -eq 0 ]]; then
        print_success "No license violations detected"
    else
        print_warning "Found $violations potential license issues to review"
    fi
}

# Function to update attribution file
update_attribution() {
    print_status "Updating LICENSE_ATTRIBUTION.md..."
    
    # Create backup
    if [[ -f "LICENSE_ATTRIBUTION.md" ]]; then
        cp "LICENSE_ATTRIBUTION.md" "LICENSE_ATTRIBUTION.md.backup"
    fi
    
    # Generate new attribution file
    pip-licenses --format=markdown --output-file="LICENSE_ATTRIBUTION.md"
    
    print_success "LICENSE_ATTRIBUTION.md updated"
}

# Function to display summary
display_summary() {
    print_status "=== License Check Summary ==="
    echo "Reports generated:"
    echo "  - Detailed: $REPORT_DIR/python_licenses_$DATE.md"
    echo "  - Summary: $REPORT_DIR/license_summary_$DATE.txt"
    echo "  - JSON: $REPORT_DIR/license_data_$DATE.json"
    echo "  - Compatibility: $REPORT_DIR/compatibility_report_$DATE.md"
    echo ""
    echo "Next steps:"
    echo "  1. Review UNKNOWN license packages"
    echo "  2. Check GPL compliance requirements"
    echo "  3. Update project documentation"
    echo "  4. Monitor for license changes"
}

# Main execution
main() {
    print_status "Starting AI Camera v2.0 License Check"
    print_status "Date: $(date)"
    echo ""
    
    # Check prerequisites
    check_venv
    activate_venv
    install_checkers
    create_report_dir
    
    # Generate reports
    generate_reports
    analyze_compatibility
    check_violations
    update_attribution
    
    # Display summary
    echo ""
    display_summary
    
    print_success "License check completed successfully!"
}

# Handle command line arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --quick        Quick check (summary only)"
        echo "  --full         Full analysis (default)"
        echo ""
        echo "This script analyzes Python dependencies and generates license compliance reports."
        exit 0
        ;;
    --quick)
        print_status "Running quick license check..."
        check_venv
        activate_venv
        create_report_dir
        pip-licenses --format=plain | head -20
        print_success "Quick check completed"
        exit 0
        ;;
    --full|"")
        main
        ;;
    *)
        print_error "Unknown option: $1"
        echo "Use --help for usage information"
        exit 1
        ;;
esac
