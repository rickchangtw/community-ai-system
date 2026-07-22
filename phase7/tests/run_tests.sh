#!/bin/bash
# Integration Test Runner
# Phase 7: Integration Testing

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
REPORT_FILE="${PROJECT_DIR}/reports/integration_test_report.md"

# Create reports directory
mkdir -p "${PROJECT_DIR}/reports"

# Test suites
TESTS=(
    "01-agent-communication"
    "02-event-triggers"
    "03-notification-routing"
    "04-database-operations"
    "05-error-handling"
)

# Initialize report
echo "# Phase 7: Integration Test Report" > "${REPORT_FILE}"
echo "" >> "${REPORT_FILE}"
echo "**Generated:** $(date)" >> "${REPORT_FILE}"
echo "" >> "${REPORT_FILE}"

PASS_TOTAL=0
FAIL_TOTAL=0

echo "========================================"
echo "Phase 7: Integration Testing"
echo "========================================"
echo ""

for test_suite in "${TESTS[@]}"; do
    echo "Running: ${test_suite}..."
    echo ""

    # Run test suite
    python3 "${SCRIPT_DIR}/${test_suite}.py"
    result=$?

    # Update report
    if [ $result -eq 0 ]; then
        echo "✓ ${test_suite}: PASSED" >> "${REPORT_FILE}"
        PASS_TOTAL=$((PASS_TOTAL + 1))
    else
        echo "✗ ${test_suite}: FAILED" >> "${REPORT_FILE}"
        FAIL_TOTAL=$((FAIL_TOTAL + 1))
    fi

    echo ""
done

# Summary
echo "========================================"
echo "Summary"
echo "========================================"
echo ""
echo "Passed: ${PASS_TOTAL}"
echo "Failed: ${FAIL_TOTAL}"
echo "Total:  $((PASS_TOTAL + FAIL_TOTAL))"
echo ""

# Update report
echo "" >> "${REPORT_FILE}"
echo "## Summary" >> "${REPORT_FILE}"
echo "" >> "${REPORT_FILE}"
echo "- **Passed:** ${PASS_TOTAL}" >> "${REPORT_FILE}"
echo "- **Failed:** ${FAIL_TOTAL}" >> "${REPORT_FILE}"
echo "- **Total:** $((PASS_TOTAL + FAIL_TOTAL))" >> "${REPORT_FILE}"

if [ $FAIL_TOTAL -eq 0 ]; then
    echo ""
    echo "✓ All integration tests passed!"
    echo ""
    echo "Report saved to: ${REPORT_FILE}"
    exit 0
else
    echo ""
    echo "✗ Some integration tests failed!"
    echo ""
    echo "Report saved to: ${REPORT_FILE}"
    exit 1
fi
