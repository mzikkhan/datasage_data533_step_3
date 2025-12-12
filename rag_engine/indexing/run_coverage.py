"""
Coverage Analysis Script for RAG Engine Indexing Module using Coverage.py.
"""

import sys
import os
import unittest


def main():
    """
    Run tests with coverage.py measurement.
    1. Import and configure coverage
    2. Start measurement
    3. Run tests
    4. Stop measurement
    5. Save data
    6. Generate reports
    """
    
    print("=" * 80)
    print("RAG ENGINE - INDEXING MODULE COVERAGE ANALYSIS")
    print("=" * 80)
    print()
    
    # Step 1: Import coverage
    print("Step 1: Importing coverage.py")
    print("-" * 80)
    try:
        import coverage
        print(f"Coverage.py version {coverage.__version__} loaded")
    except ImportError:
        print("Coverage.py not found. Installing...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "coverage"])
        import coverage
        print(f"Coverage.py installed successfully")
    print()
    
    # Step 2: Configure coverage
    print("Step 2: Configuring coverage measurement")
    print("-" * 80)
    
    # Get paths
    test_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(test_dir)
    source_dir = os.path.join(parent_dir, 'rag_engine', 'indexing')
    
    print(f"Test directory:   {test_dir}")
    print(f"Source directory: {source_dir}")
    print()
    
    # Create Coverage instance with proper configuration
    # According to docs: Coverage(source=..., omit=...)
    cov = coverage.Coverage(
        source=[source_dir],
        omit=[
            '*/tests/*',
            '*/test_*.py',
            '*/__init__.py',
            '*/__pycache__/*'
        ]
    )
    
    print("✓ Coverage configured")
    print("  - Source: rag_engine/indexing/")
    print("  - Omitting: tests, test files, __init__.py")
    print()
    
    # Step 3: Start coverage measurement
    print("Step 3: Starting coverage measurement")
    print("-" * 80)
    cov.start()
    print("✓ Coverage measurement started")
    print()
    
    # Step 4: Run tests
    print("Step 4: Running test suite")
    print("-" * 80)
    
    # Change to test directory
    original_dir = os.getcwd()
    os.chdir(test_dir)
    
    # Discover and load tests
    loader = unittest.TestLoader()
    suite = loader.discover(test_dir, pattern='test_*.py')
    
    test_count = suite.countTestCases()
    print(f"Discovered {test_count} tests")
    print()
    
    # Run tests with verbosity
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return to original directory
    os.chdir(original_dir)
    
    print()
    
    # Step 5: Stop coverage and save
    print("Step 5: Stopping coverage measurement")
    print("-" * 80)
    cov.stop()
    print("Coverage measurement stopped")
    
    # Save coverage data to .coverage file
    cov.save()
    print("Coverage data saved to .coverage file")
    print()
    
    # Step 6: Generate reports
    print("=" * 80)
    print("Step 6: Generating Coverage Reports")
    print("=" * 80)
    print()
    
    # 6a. Console report
    print("6a. Console Report (summary)")
    print("-" * 80)
    total = cov.report()
    print("-" * 80)
    print(f"TOTAL COVERAGE: {total:.1f}%")
    
    if total >= 75.0:
        print("MEETS 75% REQUIREMENT")
    else:
        print(f"BELOW 75% REQUIREMENT (need {75.0 - total:.1f}% more)")
    print()
    
    # 6b. Detailed report with missing lines
    print("6b. Detailed Report (with missing lines)")
    print("-" * 80)
    cov.report(show_missing=True)
    print()
    
    # 6c. HTML report
    print("6c. HTML Report")
    print("-" * 80)
    try:
        html_dir = os.path.join(test_dir, 'htmlcov')
        cov.html_report(directory=html_dir)
        print(f"HTML report generated: {html_dir}/index.html")
        print("Open this file in a browser to see detailed line-by-line coverage")
    except Exception as e:
        print(f"Failed to generate HTML report: {e}")
    print()
    
    # 6d. XML report
    print("6d. XML Report")
    print("-" * 80)
    try:
        xml_file = os.path.join(test_dir, 'coverage.xml')
        cov.xml_report(outfile=xml_file)
        print(f"XML report generated: {xml_file}")
    except Exception as e:
        print(f"Failed to generate XML report: {e}")
    print()
    
    # Step 7: Analyze specific modules
    print("=" * 80)
    print("Step 7: Per-Module Coverage Analysis")
    print("=" * 80)
    print()
    
    # Get measured files
    data = cov.get_data()
    measured_files = data.measured_files()
    
    modules = {
        'embedder.py': None,
        'vector_store.py': None,
        'index_engine.py': None
    }
    
    # Find matching files
    for filename in measured_files:
        for module_name in modules.keys():
            if module_name in filename:
                modules[module_name] = filename
                break
    
    # Analyze each module
    for module_name, filepath in modules.items():
        if filepath:
            try:
                # Get analysis for this file
                analysis = cov.analysis(filepath)
                
                # analysis returns: (filename, executed_lines, missing_lines, excluded_lines)
                executed = set(analysis[1])
                missing = set(analysis[2])
                
                total_lines = len(executed) + len(missing)
                coverage_pct = (len(executed) / total_lines * 100) if total_lines > 0 else 0
                
                print(f"{module_name}:")
                print(f"  File: {filepath}")
                print(f"  Total lines:     {total_lines}")
                print(f"  Executed lines:  {len(executed)}")
                print(f"  Missing lines:   {len(missing)}")
                print(f"  Coverage:        {coverage_pct:.1f}%")
                
                if coverage_pct >= 75.0:
                    print(f"  Status: MEETS 75% REQUIREMENT")
                else:
                    print(f"  Status: BELOW 75% (need {75.0 - coverage_pct:.1f}% more)")
                
                # Show some missing lines (up to 10)
                if missing:
                    missing_list = sorted(list(missing))[:10]
                    if len(missing) <= 10:
                        print(f"  Missing lines:   {missing_list}")
                    else:
                        print(f"  Missing lines:   {missing_list} ... and {len(missing) - 10} more")
                
                print()
                
            except Exception as e:
                print(f"{module_name}: Error analyzing - {e}")
                print()
        else:
            print(f"{module_name}: Not found in coverage data")
            print()
    
    # Step 8: Test results summary
    print("=" * 80)
    print("Step 8: Test Results Summary")
    print("=" * 80)
    print()
    
    print(f"Tests run:    {result.testsRun}")
    print(f"Successes:    {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures:     {len(result.failures)}")
    print(f"Errors:       {len(result.errors)}")
    print(f"Skipped:      {len(result.skipped)}")
    print()
    
    if result.wasSuccessful():
        print("ALL TESTS PASSED")
    else:
        print("SOME TESTS FAILED")
        if result.failures:
            print("\nFailed tests:")
            for test, traceback in result.failures:
                print(f"  - {test}")
        if result.errors:
            print("\nTests with errors:")
            for test, traceback in result.errors:
                print(f"  - {test}")
    
    print()
    
    # Final summary
    print("=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)
    print()
    
    tests_passed = result.wasSuccessful()
    coverage_met = total >= 75.0
    
    print(f"Tests:    {'PASSED' if tests_passed else '✗ FAILED'}")
    print(f"Coverage: {'MEETS REQUIREMENT (≥75%)' if coverage_met else '✗ BELOW REQUIREMENT (<75%)'}")
    print(f"Total:    {total:.1f}%")
    print()
    
    print("Generated files:")
    print(f"  - .coverage (coverage data)")
    print(f"  - htmlcov/index.html (interactive report)")
    print(f"  - coverage.xml (XML report)")
    print()
    
    print("=" * 80)
    
    # Return appropriate exit code
    if tests_passed and coverage_met:
        print("SUCCESS: All requirements met")
        return 0
    else:
        print("FAILURE: Some requirements not met")
        return 1


if __name__ == '__main__':
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)