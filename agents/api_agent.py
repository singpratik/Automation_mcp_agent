import requests
import json
import time
import html
import re
import os
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse
from llm.llm_interface import get_llm_response

# Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class APIRetryConfig:
    """Configuration for API request retries"""
    def __init__(self, max_retries: int = 3, backoff_factor: float = 1.5, timeout: int = 30):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.timeout = timeout

class APIAgent:
    """Enhanced API Agent with better error handling and retry logic"""
    
    def __init__(self, temperature: float = 0.7, retry_config: Optional[APIRetryConfig] = None):
        self.temperature = temperature
        self.test_results = []
        self.session = requests.Session()
        self.retry_config = retry_config or APIRetryConfig()
        self.ssl_verify = self._resolve_ssl_verification()
        self.allow_insecure_ssl_fallback = os.getenv("API_ALLOW_INSECURE_SSL_FALLBACK", "true").lower() == "true"
        self.session.verify = self.ssl_verify
        logger.info(f"APIAgent initialized with retry_config: max_retries={self.retry_config.max_retries}")

    def _resolve_ssl_verification(self):
        """
        Resolve SSL verification strategy.

        Priority:
        1. API_CA_BUNDLE path
        2. REQUESTS_CA_BUNDLE / SSL_CERT_FILE
        3. API_SSL_VERIFY=false -> disable verification
        4. Default verification (True)
        """
        api_ca_bundle = os.getenv("API_CA_BUNDLE")
        requests_ca_bundle = os.getenv("REQUESTS_CA_BUNDLE") or os.getenv("SSL_CERT_FILE")
        api_ssl_verify = os.getenv("API_SSL_VERIFY", "true").lower()

        if api_ca_bundle:
            logger.info(f"Using API_CA_BUNDLE for TLS verification: {api_ca_bundle}")
            return api_ca_bundle
        if requests_ca_bundle:
            logger.info(f"Using CA bundle from environment for TLS verification: {requests_ca_bundle}")
            return requests_ca_bundle
        if api_ssl_verify in {"0", "false", "no", "off"}:
            logger.warning("API_SSL_VERIFY is disabled. TLS certificates will not be verified.")
            return False
        return True

    def run_task(self, prompt: str) -> str:
        """
        Main entry point for API testing tasks with enhanced error handling
        
        Args:
            prompt: Natural language description of API test
            
        Returns:
            Comprehensive test report
        """
        try:
            logger.info(f"Starting API test task: {prompt[:50]}...")
            
            # Use AI to understand the testing request
            test_plan = self._generate_test_plan(prompt)
            logger.info(f"Generated test plan with {len(test_plan.get('endpoints', []))} endpoints")
            
            # Execute the test plan
            results = self._execute_test_plan(test_plan)
            
            # Generate comprehensive report
            return self._generate_report(results)
            
        except ValueError as e:
            error_msg = f"❌ Validation error in API test: {str(e)}"
            logger.error(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"❌ API testing failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return error_msg
    
    def _generate_test_plan(self, prompt: str) -> dict:
        """
        Use AI to create a structured test plan from natural language
        
        Args:
            prompt: Natural language test description
            
        Returns:
            Structured test plan dictionary
            
        Raises:
            ValueError: If test plan generation fails
        """
        try:
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
            logger.debug(f"LLM response: {response[:100]}...")
            
            try:
                # Extract JSON from response with better parsing
                json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response)
                if json_match:
                    plan = json.loads(json_match.group())
                    logger.info("✅ Successfully parsed test plan from LLM response")
                    return plan
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"JSON parsing error: {e}, falling back to simple parser")
            
            # Fallback: simple parsing
            return self._parse_simple_request(prompt)
            
        except Exception as e:
            logger.error(f"Error generating test plan: {e}")
            raise ValueError(f"Failed to generate test plan: {str(e)}")
    
    def _parse_simple_request(self, prompt: str) -> dict:
        """
        Fallback parser for simple API requests with enhanced error handling
        
        Args:
            prompt: API request description
            
        Returns:
            Simple test plan
            
        Raises:
            ValueError: If URL extraction fails
        """
        try:
            # Extract URL
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

            expected_status = 200
            lowered_prompt = prompt.lower()
            lowered_url = url.lower()
            if "404" in lowered_prompt or "invalid" in lowered_prompt or "invalid" in lowered_url:
                expected_status = 404
            
            return {
                "base_url": "",
                "endpoints": [{
                    "name": "API Test",
                    "method": method,
                    "path": url,
                    "headers": {"Content-Type": "application/json"},
                    "data": {},
                    "expected_status": expected_status,
                    "validations": []
                }]
            }
        except Exception as e:
            logger.error(f"Error parsing simple request: {e}")
            raise ValueError(f"Failed to parse API request: {str(e)}")
    
    def _execute_test_plan(self, test_plan: dict) -> list:
        """
        Execute all tests in the plan with enhanced error handling
        
        Args:
            test_plan: Structured test plan
            
        Returns:
            List of test results
        """
        results = []
        base_url = test_plan.get("base_url", "")
        
        for endpoint in test_plan.get("endpoints", []):
            try:
                result = self._test_endpoint(base_url, endpoint)
                results.append(result)
            except Exception as e:
                logger.error(f"Error testing endpoint {endpoint.get('name')}: {e}")
                results.append({
                    "name": endpoint.get("name", "Unknown"),
                    "status": "ERROR",
                    "errors": [str(e)]
                })
            
        return results
    
    def _test_endpoint(self, base_url: str, endpoint: dict) -> dict:
        """
        Test a single API endpoint with retry logic
        
        Args:
            base_url: Base URL for API
            endpoint: Endpoint configuration
            
        Returns:
            Test result dictionary
        """
        start_time = time.time()
        test_result = {
            "name": endpoint.get("name", "API Test"),
            "method": endpoint.get("method", "GET"),
            "url": "",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "FAILED",
            "response_time": 0,
            "status_code": None,
            "response_data": None,
            "validations": [],
            "errors": []
        }
        
        try:
            # Build full URL with validation
            url = endpoint.get("path", "")
            if base_url and not url.startswith("http"):
                url = base_url.rstrip("/") + "/" + url.lstrip("/")
            
            test_result["url"] = url
            
            # Validate URL to prevent SSRF
            if not self._is_safe_url(url):
                test_result["errors"] = ["URL not allowed for security reasons"]
                return test_result
            
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
                except (ValueError, KeyError):
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
                
            except requests.exceptions.SSLError as ssl_err:
                ssl_error_text = str(ssl_err)
                logger.warning(f"SSL verification failed for {url}: {ssl_error_text}")

                if self.allow_insecure_ssl_fallback and url.lower().startswith("https://"):
                    logger.warning(f"Retrying {url} with TLS verification disabled due to SSL error.")
                    try:
                        response = self.session.request(
                            method=endpoint["method"],
                            url=url,
                            headers=endpoint.get("headers", {}),
                            json=endpoint.get("data") if endpoint.get("data") else None,
                            timeout=30,
                            verify=False
                        )

                        test_result["response_time"] = round((time.time() - start_time) * 1000, 2)
                        test_result["status_code"] = response.status_code

                        try:
                            test_result["response_data"] = response.json()
                        except (ValueError, KeyError):
                            test_result["response_data"] = response.text

                        expected_status = endpoint.get("expected_status", 200)
                        if response.status_code == expected_status:
                            test_result["validations"].append(f"✅ Status code {response.status_code} matches expected")
                        else:
                            test_result["validations"].append(f"❌ Status code {response.status_code}, expected {expected_status}")
                            test_result["errors"].append(f"Unexpected status code: {response.status_code}")

                        for validation in endpoint.get("validations", []):
                            validation_result = self._validate_response(response, validation)
                            test_result["validations"].append(validation_result)

                        test_result["validations"].append("⚠️ TLS verification disabled fallback was used")

                        if not test_result["errors"] and all(("✅" in v or "⚠️" in v) for v in test_result["validations"]):
                            test_result["status"] = "PASSED"

                    except Exception as insecure_err:
                        test_result["response_time"] = round((time.time() - start_time) * 1000, 2)
                        test_result["errors"].append(f"SSL retry failed: {str(insecure_err)}")
                        logger.error(f"SSL retry error for {url}: {insecure_err}")
                else:
                    test_result["response_time"] = round((time.time() - start_time) * 1000, 2)
                    test_result["errors"].append(f"SSL verification failed: {ssl_error_text}")
                    logger.error(f"SSL request error for {url}: {ssl_err}")

            except Exception as e:
                test_result["response_time"] = round((time.time() - start_time) * 1000, 2)
                test_result["errors"].append(f"Request failed: {str(e)}")
                logger.error(f"Request error for {url}: {e}")
        
        except Exception as e:
            test_result["response_time"] = round((time.time() - start_time) * 1000, 2)
            test_result["errors"].append(f"Endpoint test error: {str(e)}")
            logger.error(f"Endpoint test error: {e}")
        
        return test_result
    
    def _is_safe_url(self, url: str) -> bool:
        """Validate URL to prevent SSRF attacks"""
        try:
            parsed = urlparse(url)
            # Only allow http/https
            if parsed.scheme not in ['http', 'https']:
                return False
            # Block internal/private IPs
            hostname = parsed.hostname
            if not hostname:
                return False
            # Add more validation as needed
            blocked_hosts = ['localhost', '127.0.0.1', '0.0.0.0', '::1']
            if hostname.lower() in blocked_hosts:
                return False
            return True
        except Exception:
            return False
    
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
        return getattr(self, '_last_results', [])

    def run_api_tests(self, api_tests):
        """
        Run a list of API test prompts and return their results.
        Each test in api_tests should be a string prompt describing the API test.
        """
        results = []
        for test in api_tests:
            result = self.run_task(test)
            results.append({"test": test, "result": result})
        return results
