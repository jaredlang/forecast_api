#!/bin/bash
# Test runner script for Weather Forecast API

set -e

echo "========================================"
echo "Weather Forecast API - Test Runner"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_step() {
    echo -e "${BLUE}==>${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}!${NC} $1"
}

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    print_warning "pytest not found. Installing test dependencies..."
    pip install -r requirements.txt
fi

# Parse command line arguments
TEST_TYPE=${1:-"all"}

case $TEST_TYPE in
    "unit"|"pytest")
        print_step "Running unit tests with pytest..."
        pytest -v
        print_success "Unit tests completed!"
        ;;

    "weather")
        print_step "Running weather endpoint tests..."
        pytest tests/test_weather.py -v
        print_success "Weather tests completed!"
        ;;

    "stats")
        print_step "Running stats endpoint tests..."
        pytest tests/test_stats.py -v
        print_success "Stats tests completed!"
        ;;

    "health")
        print_step "Running health endpoint tests..."
        pytest tests/test_health.py -v
        print_success "Health tests completed!"
        ;;

    "manual")
        API_URL=${2:-"http://localhost:8000"}
        print_step "Running manual integration tests against $API_URL..."
        print_warning "Make sure the API server is running!"
        python tests/manual_test.py $API_URL
        ;;

    "coverage")
        print_step "Running tests with coverage report..."
        if ! command -v pytest-cov &> /dev/null; then
            print_warning "pytest-cov not found. Installing..."
            pip install pytest-cov
        fi
        pytest --cov=. --cov-report=html --cov-report=term
        print_success "Coverage report generated in htmlcov/"
        ;;

    "all")
        print_step "Running all unit tests..."
        pytest -v
        print_success "All unit tests completed!"
        echo ""
        print_warning "To run manual integration tests, use: ./run_tests.sh manual"
        ;;

    *)
        echo "Usage: ./run_tests.sh [test_type] [options]"
        echo ""
        echo "Test types:"
        echo "  all         - Run all unit tests (default)"
        echo "  unit|pytest - Run all unit tests"
        echo "  weather     - Run weather endpoint tests only"
        echo "  stats       - Run stats endpoint tests only"
        echo "  health      - Run health endpoint tests only"
        echo "  manual [url] - Run manual integration tests (requires running server)"
        echo "  coverage    - Run tests with coverage report"
        echo ""
        echo "Examples:"
        echo "  ./run_tests.sh"
        echo "  ./run_tests.sh unit"
        echo "  ./run_tests.sh weather"
        echo "  ./run_tests.sh manual http://localhost:8000"
        echo "  ./run_tests.sh coverage"
        exit 1
        ;;
esac

echo ""
echo "========================================"
echo "Tests completed successfully!"
echo "========================================"
