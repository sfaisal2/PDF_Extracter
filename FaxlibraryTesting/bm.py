import os
import re
import json
from datetime import datetime
import pandas as pd

class InsuranceFaxBenchmark:
    """Benchmark test for insurance fax extraction accuracy"""
    
    def __init__(self, markdown_dir="."):
        self.markdown_dir = markdown_dir
        self.results = []
        
    def load_markdown_file(self, filename):
        """Load markdown content from file"""
        filepath = os.path.join(self.markdown_dir, filename)
        if not os.path.exists(filepath):
            # Try without .md extension
            if not filepath.endswith('.md'):
                filepath += '.md'
            if not os.path.exists(filepath):
                return None
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
        return None
    
    def test_umr(self, content):
        """Test UMR fax extraction"""
        tests = {
            "Patient Name": ("Sheriff Olaleye", bool(re.search(r"Sheriff\s+Olaleye", content, re.IGNORECASE))),
            "Member ID": ("21213115", "21213115" in content),
            "Group Number": ("76414056", "76414056" in content),
            "Annual Maximum": ("$2,500.00", "$2,500.00" in content or "2500.00" in content),
            "Deductible": ("$50.00", "$50.00" in content or "50.00" in content),
            "Preventive Coverage": ("100%", "100%" in content and any(word in content.lower() for word in ["preventive", "diagnostic"])),
            "Basic Coverage": ("80%", "80%" in content and "basic" in content.lower()),
            "Major Coverage": ("50%", "50%" in content and "major" in content.lower()),
            "Tables Extracted": ("Yes", content.count("\n|---") > 2),  # Check for markdown tables
        }
        return tests
    
    def test_guardian(self, content):
        """Test Guardian fax extraction"""
        tests = {
            "Patient Name": ("HARDEN, LISA", bool(re.search(r"HARDEN,\s*LISA", content, re.IGNORECASE))),
            "Group Number": ("00569654", "00569654" in content),
            "Plan Name": ("Dentalguard Preferred", "Dentalguard Preferred" in content),
            "Annual Maximum": ("$1200.00", "$1200.00" in content or "1200.00" in content),
            "Deductible": ("$50.00", "$50.00" in content or "50.00" in content),
            "Cleaning Coverage": ("100%", "100%" in content and any(word in content.lower() for word in ["cleaning", "prophylaxis"])),
            "Crown Coverage": ("60%", "60%" in content and "crown" in content.lower()),
            "Procedure Codes": ("Yes", bool(re.search(r"D\d{4}", content))),  # CDT codes
            "Tables Extracted": ("Yes", content.count("\n|---") > 5),
        }
        return tests
    
    def test_delta(self, content):
        """Test Delta Dental fax extraction"""
        tests = {
            "Patient Name": ("Boone Kelly", bool(re.search(r"Boone\s+Kelly", content, re.IGNORECASE))),
            "Member ID": ("116798836901", "116798836901" in content),
            "Group Number": ("21036-10000", "21036-10000" in content),
            "Annual Maximum": ("$2000.00", "$2000.00" in content or "2000.00" in content),
            "Orthodontic Maximum": ("$1500.00", "$1500.00" in content or "1500.00" in content),
            "Deductible": ("$50.00", "$50.00" in content or "50.00" in content),
            "Procedure Tables": ("Yes", bool(re.search(r"D0120.*?100%", content, re.DOTALL))),
        }
        return tests
    
    def test_bcbs(self, content):
        """Test BCBS fax extraction"""
        tests = {
            "Patient Name": ("TREJO-CRUZ, ANTHONY", bool(re.search(r"TREJO-CRUZ,\s*ANTHONY", content, re.IGNORECASE))),
            "Member ID": ("837018352", "837018352" in content),
            "Group Number": ("019855", "019855" in content),
            "Annual Maximum": ("$2000.00", "$2000.00" in content or "2000.00" in content),
            "Deductible": ("$50.00", "$50.00" in content or "50.00" in content),
            "Network Info": ("Yes", any(word in content.lower() for word in ["in network", "out of network", "ppo"])),
        }
        return tests
    
    def test_apl(self, content):
        """Test APL fax extraction"""
        tests = {
            "Patient Name": ("GABRIELLE HENDERSON", bool(re.search(r"GABRIELLE\s+HENDERSON", content, re.IGNORECASE))),
            "Policy Number": ("02113886", "02113886" in content),
            "Annual Maximum": ("$1500.00", "$1500.00" in content or "1500.00" in content),
            "Deductible": ("$50.00", "$50.00" in content or "50.00" in content),
            "Preventive Coverage": ("100%", "100%" in content and "preventive" in content.lower()),
            "Procedure Codes": ("Yes", bool(re.search(r"\b0\d{4}\b", content))),  # APL uses 5-digit codes
            "Limitations Key": ("Yes", "Limitations:" in content),
        }
        return tests
    
    def run_all_tests(self):
        """Run tests on all markdown files"""
        test_files = {
            "UMR.pdf": self.test_umr,
            "Guardian.pdf": self.test_guardian,
            "Delta.pdf": self.test_delta,
            "BCBS.pdf": self.test_bcbs,
            "apl.pdf": self.test_apl,
        }
        
        print("📊 INSURANCE FAX EXTRACTION BENCHMARK")
        print("=" * 70)
        
        for filename, test_func in test_files.items():
            print(f"\n🔍 Testing: {filename}")
            
            # Try different naming patterns
            markdown_content = None
            for pattern in [
                filename.replace('.pdf', '.md'),
                filename.replace('.pdf', '_converted.md'),
                filename + '.md',
                filename
            ]:
                markdown_content = self.load_markdown_file(pattern)
                if markdown_content:
                    break
            
            if not markdown_content:
                print(f"   ❌ No markdown file found for {filename}")
                self.results.append({
                    "file": filename,
                    "status": "File not found",
                    "accuracy": 0
                })
                continue
            
            # Run specific tests
            tests = test_func(markdown_content)
            
            # Calculate results
            passed = sum(1 for _, (_, result) in tests.items() if result)
            total = len(tests)
            accuracy = (passed / total) * 100 if total > 0 else 0
            
            # Store results
            file_result = {
                "file": filename,
                "status": "Success",
                "accuracy": accuracy,
                "passed": passed,
                "total": total,
                "details": {}
            }
            
            print(f"   ✅ Accuracy: {accuracy:.1f}% ({passed}/{total})")
            
            # Show individual test results
            for test_name, (expected, result) in tests.items():
                status = "✓" if result else "✗"
                file_result["details"][test_name] = {
                    "expected": expected,
                    "passed": result
                }
                if not result:
                    print(f"      {status} {test_name}: Expected '{expected}'")
            
            self.results.append(file_result)
        
        return self.generate_summary_report()
    
    def generate_summary_report(self):
        """Generate summary report"""
        print("\n" + "=" * 70)
        print("SUMMARY REPORT")
        print("=" * 70)
        
        if not self.results:
            print("No results to report")
            return
        
        total_passed = sum(r.get("passed", 0) for r in self.results if r.get("status") == "Success")
        total_tests = sum(r.get("total", 0) for r in self.results if r.get("status") == "Success")
        overall_accuracy = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📈 Overall Accuracy: {overall_accuracy:.1f}%")
        print(f"📈 Total Tests: {total_passed}/{total_tests}")
        
        # Create DataFrame for better viewing
        df_data = []
        for result in self.results:
            if result["status"] == "Success":
                df_data.append({
                    "File": result["file"],
                    "Accuracy": f"{result['accuracy']:.1f}%",
                    "Passed": f"{result['passed']}/{result['total']}",
                    "Status": "✅" if result['accuracy'] >= 80 else "⚠️" if result['accuracy'] >= 50 else "❌"
                })
        
        if df_data:
            df = pd.DataFrame(df_data)
            print("\n📋 Detailed Results:")
            print(df.to_string(index=False))
        
        # Identify common issues
        print("\n🔍 Common Issues Found:")
        common_issues = []
        
        for result in self.results:
            if result["status"] == "Success" and result["accuracy"] < 100:
                failed_tests = [k for k, v in result["details"].items() if not v["passed"]]
                if failed_tests:
                    common_issues.append(f"{result['file']}: {', '.join(failed_tests[:3])}")
        
        if common_issues:
            for issue in common_issues[:5]:  # Show top 5
                print(f"   • {issue}")
        else:
            print("   • No common issues found")
        
        # Save results to JSON
        output_file = f"benchmark_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to: {output_file}")
        
        return {
            "overall_accuracy": overall_accuracy,
            "total_passed": total_passed,
            "total_tests": total_tests,
            "files_tested": len([r for r in self.results if r["status"] == "Success"])
        }

# ============================================================================
# QUICK VALIDATION TEST (Simplified)
# ============================================================================

def quick_validation(markdown_content, filename):
    """Quick validation of key data points"""
    print(f"\n🔍 Quick Validation: {filename}")
    print("-" * 50)
    
    # Basic checks
    checks = [
        ("Has Patient Name", bool(re.search(r"patient.*name|member.*name", markdown_content, re.IGNORECASE))),
        ("Has Financial Info", bool(re.search(r"\$\d+\.?\d*|maximum|deductible", markdown_content))),
        ("Has Coverage %", bool(re.search(r"\d+%", markdown_content))),
        ("Has Tables", markdown_content.count("\n|---") > 0),
        ("Has Dates", bool(re.search(r"\d{1,2}/\d{1,2}/\d{4}|\d{4}-\d{2}-\d{2}", markdown_content))),
    ]
    
    for check_name, result in checks:
        status = "✓" if result else "✗"
        print(f"   {status} {check_name}")
    
    # File-specific checks
    if "umr" in filename.lower():
        print(f"   UMR Specific: {'Sheriff Olaleye' in markdown_content}")
    elif "guardian" in filename.lower():
        print(f"   Guardian Specific: {'Dentalguard' in markdown_content}")
    elif "delta" in filename.lower():
        print(f"   Delta Specific: {'Boone Kelly' in markdown_content}")
    
    return len([c for _, c in checks if c])

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Initialize benchmark
    benchmark = InsuranceFaxBenchmark()
    
    # Option 1: Run comprehensive benchmark
    print("Running comprehensive benchmark...")
    results = benchmark.run_all_tests()
    
    # Option 2: Quick check specific files
    print("\n" + "=" * 70)
    print("QUICK VALIDATION CHECKS")
    print("=" * 70)
    
    files_to_check = ["UMR.md", "Guardian.md", "Delta.md", "BCBS.md", "apl.md"]
    
    for filename in files_to_check:
        content = benchmark.load_markdown_file(filename)
        if content:
            score = quick_validation(content, filename)
            print(f"   Score: {score}/5")
        else:
            print(f"   File not found: {filename}")
    
    print("\n✅ Benchmark complete!")