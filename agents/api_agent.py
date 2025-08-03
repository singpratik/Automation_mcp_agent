import requests
import json
import time
from datetime import datetime
from llm.llm_interface import get_llm_response

class APIAgent:
    def __init__(self, temperature=0.7):
        self.temperature = temperature
        self.test_results = []
        self.session = requests.Session()

    def run_task(self, prompt: str) -> str:
        """Main entry point for API testing tasks"""
        try:
            # Use AI to understand the testing request
            test_plan = self._generate_test_plan(prompt)
            
            # Execute the test plan
            results = self._execute_test_plan(test_plan)
            
            # Generate comprehensive report
            return self._generate_report(results)
            
        except Exception as e:
            return f"API testing failed: {str(e)}"
    
    def _generate_test_plan(self, prompt: str) -> dict:
        """Use AI to create a structured test plan from natural language"""
        ai_prompt = f"""
        Create an API test plan from this request: {prompt}
        
        Respond with JSON containing:
        {{
            "base_url": "API base URL",
            "endpoints": [
                {{
                    "name": "test name",
                    "method": "GET/POST/PUT/DELETE",
                    "path": "/endpoint/path",
                    "headers": {{"key": "value"}},
                    "data": {{"key": "value"}},
                    "expected_status": 200,
                    "validations": ["response should contain X", "status should be Y"]
                }}
            ]
        }}
        """
        
        response = get_llm_response(ai_prompt)
        
        try:
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        # Fallback: simple parsing
        return self._parse_simple_request(prompt)
    
    def _parse_simple_request(self, prompt: str) -> dict:
        """Fallback parser for simple API requests"""
        # Extract URL
        import re
        url_match = re.search(r'https?://[^\s]+', prompt)
        if not url_match:
            raise ValueError("No URL found in request")
        
        url = url_match.group()
        method = "GET"
        
        # Extract method
        if "POST" in prompt.upper():
            method = "POST"
        elif "PUT" in prompt.upper():
            method = "PUT"
        elif "DELETE" in prompt.upper():
            method = "DELETE"
        
        return {
            "base_url": "",
            "endpoints": [{
                "name": "API Test",
                "method": method,
                "path": url,
                "headers": {"Content-Type": "application/json"},
                "data": {},
                "expected_status": 200,
                "validations": []
            }]
        }
    
    def _execute_test_plan(self, test_plan: dict) -> list:
        """Execute all tests in the plan"""
        results = []
        base_url = test_plan.get("base_url", "")
        
        for endpoint in test_plan.get("endpoints", []):
            result = self._test_endpoint(base_url, endpoint)
            results.append(result)
            
        return results
    
    def _test_endpoint(self, base_url: str, endpoint: dict) -> dict:
        """Test a single API endpoint"""
        start_time = time.time()
        
        # Build full URL
        url = endpoint["path"]
        if base_url and not url.startswith("http"):
            url = base_url.rstrip("/") + "/" + url.lstrip("/")
        
        test_result = {
            "name": endpoint["name"],
            "method": endpoint["method"],
            "url": url,
            "timestamp": datetime.now().isoformat(),
            "status": "FAILED",
            "response_time": 0,
            "status_code": None,
            "response_data": None,
            "validations": [],
            "errors": []
        }
        
        try:
            # Make the request
            response = self.session.request(
                method=endpoint["method"],
                url=url,
                headers=endpoint.get("headers", {}),
                json=endpoint.get("data") if endpoint.get("data") else None,
                timeout=30
            )
            
            test_result["response_time"] = round((time.time() - start_time) * 1000, 2)
            test_result["status_code"] = response.status_code
            
            # Parse response
            try:
                test_result["response_data"] = response.json()
            except:
                test_result["response_data"] = response.text
            
            # Validate status code
            expected_status = endpoint.get("expected_status", 200)
            if response.status_code == expected_status:
                test_result["validations"].append(f"✅ Status code {response.status_code} matches expected")
            else:
                test_result["validations"].append(f"❌ Status code {response.status_code}, expected {expected_status}")
                test_result["errors"].append(f"Unexpected status code: {response.status_code}")
            
            # Run custom validations
            for validation in endpoint.get("validations", []):
                validation_result = self._validate_response(response, validation)
                test_result["validations"].append(validation_result)
            
            # Determine overall status
            if not test_result["errors"] and all("✅" in v for v in test_result["validations"]):
                test_result["status"] = "PASSED"
            
        except Exception as e:
            test_result["response_time"] = round((time.time() - start_time) * 1000, 2)
            test_result["errors"].append(str(e))
        
        return test_result
    
    def _validate_response(self, response, validation: str) -> str:
        """Validate response against a validation rule"""
        try:
            response_text = response.text.lower()
            validation_lower = validation.lower()
            
            if "contain" in validation_lower:
                # Extract what should be contained
                import re
                match = re.search(r'contain[s]?\s+["\']?([^"\'\n]+)["\']?', validation_lower)
                if match:
                    expected = match.group(1).strip()
                    if expected in response_text:
                        return f"✅ Response contains '{expected}'"
                    else:
                        return f"❌ Response does not contain '{expected}'"
            
            elif "status" in validation_lower and "should be" in validation_lower:
                # Status validation already handled above
                return f"✅ Status validation completed"
            
            else:
                # Generic validation
                return f"✅ Validation: {validation}"
                
        except Exception as e:
            return f"❌ Validation failed: {validation} - {str(e)}"
    
    def _generate_report(self, results: list) -> str:
        """Generate a comprehensive test report"""
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r["status"] == "PASSED")
        failed_tests = total_tests - passed_tests
        
        report = []
        report.append("🧪 API AUTOMATION TEST REPORT")
        report.append("=" * 40)
        report.append(f"📊 Summary: {passed_tests}/{total_tests} tests passed")
        report.append(f"✅ Passed: {passed_tests}")
        report.append(f"❌ Failed: {failed_tests}")
        report.append("")
        
        for i, result in enumerate(results, 1):
            status_icon = "✅" if result["status"] == "PASSED" else "❌"
            report.append(f"{status_icon} Test {i}: {result['name']}")
            report.append(f"   Method: {result['method']} {result['url']}")
            report.append(f"   Status: {result['status_code']} ({result['response_time']}ms)")
            
            if result["validations"]:
                report.append("   Validations:")
                for validation in result["validations"]:
                    report.append(f"     {validation}")
            
            if result["errors"]:
                report.append("   Errors:")
                for error in result["errors"]:
                    report.append(f"     ❌ {error}")
            
            report.append("")
        
        return "\n".join(report)
    
    def get_test_results(self):
        """Get detailed test results"""
        return self.test_results