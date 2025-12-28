#!/usr/bin/env python3
"""
Manual test script for Weather Forecast API.
Tests all endpoints against a running API server.

Usage:
    python manual_test.py [BASE_URL]

    BASE_URL: API server URL (default: http://localhost:8080)

Examples:
    python manual_test.py
    python manual_test.py http://localhost:8080
    python manual_test.py https://weather-api.example.com
"""

import requests
import sys
import json
import base64
from datetime import datetime
from typing import Optional


class Colors:
    """Terminal colors for output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


class APITester:
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url.rstrip('/')
        self.passed = 0
        self.failed = 0

    def print_header(self, text: str):
        """Print a section header"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}\n")

    def print_success(self, text: str):
        """Print success message"""
        print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")
        self.passed += 1

    def print_error(self, text: str):
        """Print error message"""
        print(f"{Colors.RED}✗ {text}{Colors.RESET}")
        self.failed += 1

    def print_info(self, text: str):
        """Print info message"""
        print(f"{Colors.YELLOW}ℹ {text}{Colors.RESET}")

    def print_json(self, data: dict, indent: int = 2):
        """Pretty print JSON data"""
        print(json.dumps(data, indent=indent))

    def test_root_endpoint(self):
        """Test GET /"""
        self.print_header("Testing Root Endpoint: GET /")

        try:
            response = requests.get(f"{self.base_url}/")

            if response.status_code == 200:
                self.print_success(f"Root endpoint returned 200 OK")
                data = response.json()

                if "service" in data and "version" in data:
                    self.print_success(f"Response contains service info: {data['service']} v{data['version']}")
                    self.print_json(data)
                else:
                    self.print_error("Response missing service or version fields")
            else:
                self.print_error(f"Root endpoint returned {response.status_code}")

        except Exception as e:
            self.print_error(f"Root endpoint test failed: {e}")

    def test_health_endpoint(self):
        """Test GET /health"""
        self.print_header("Testing Health Endpoint: GET /health")

        try:
            response = requests.get(f"{self.base_url}/health")

            if response.status_code == 200:
                self.print_success(f"Health endpoint returned 200 OK")
                data = response.json()

                if data.get("status") == "healthy":
                    self.print_success(f"Service is healthy")
                else:
                    self.print_error(f"Service is unhealthy: {data.get('status')}")

                if data.get("database", {}).get("connected"):
                    self.print_success(f"Database connected: {data['database'].get('instance')}")
                else:
                    self.print_error(f"Database not connected: {data.get('database', {}).get('error')}")

                self.print_json(data)
            else:
                self.print_error(f"Health endpoint returned {response.status_code}")

        except Exception as e:
            self.print_error(f"Health endpoint test failed: {e}")

    def test_stats_endpoint(self):
        """Test GET /stats"""
        self.print_header("Testing Stats Endpoint: GET /stats")

        try:
            response = requests.get(f"{self.base_url}/stats")

            if response.status_code == 200:
                self.print_success(f"Stats endpoint returned 200 OK")
                data = response.json()

                if "statistics" in data:
                    stats = data["statistics"]
                    self.print_success(f"Total forecasts: {stats.get('total_forecasts', 0)}")
                    self.print_success(f"Total text size: {stats.get('total_text_bytes', 0)} bytes")
                    self.print_success(f"Total audio size: {stats.get('total_audio_bytes', 0)} bytes")

                    encodings = stats.get('encodings_used', {})
                    if encodings:
                        self.print_info(f"Encodings: {', '.join([f'{k}={v}' for k, v in encodings.items()])}")

                    languages = stats.get('languages_used', {})
                    if languages:
                        self.print_info(f"Languages: {', '.join([f'{k}={v}' for k, v in languages.items()])}")

                    self.print_json(data)
                else:
                    self.print_error("Response missing statistics field")
            elif response.status_code == 503:
                self.print_error(f"Database unavailable (503)")
                self.print_json(response.json())
            else:
                self.print_error(f"Stats endpoint returned {response.status_code}")

        except Exception as e:
            self.print_error(f"Stats endpoint test failed: {e}")

    def test_latest_forecast(self, city: str = "chicago", language: Optional[str] = None):
        """Test GET /weather/{city}"""
        endpoint = f"/weather/{city}"
        if language:
            endpoint += f"?language={language}"

        self.print_header(f"Testing Latest Forecast: GET {endpoint}")

        try:
            response = requests.get(f"{self.base_url}{endpoint}")

            if response.status_code == 200:
                self.print_success(f"Latest forecast endpoint returned 200 OK")
                data = response.json()

                if data.get("status") == "success" and "forecast" in data:
                    forecast = data["forecast"]
                    self.print_success(f"Forecast retrieved for city: {data.get('city')}")
                    self.print_info(f"Forecast time: {forecast.get('forecast_at')}")
                    self.print_info(f"Expires at: {forecast.get('expires_at')}")
                    self.print_info(f"Age: {forecast.get('age_seconds')} seconds")

                    metadata = forecast.get("metadata", {})
                    self.print_info(f"Encoding: {metadata.get('encoding')}")
                    self.print_info(f"Language: {metadata.get('language')}")
                    self.print_info(f"Locale: {metadata.get('locale')}")

                    sizes = metadata.get("sizes", {})
                    self.print_info(f"Text size: {sizes.get('text_bytes')} bytes")
                    self.print_info(f"Audio size: {sizes.get('audio_bytes')} bytes")

                    # Verify base64 audio
                    audio_b64 = forecast.get("audio_base64")
                    if audio_b64:
                        try:
                            audio_bytes = base64.b64decode(audio_b64)
                            self.print_success(f"Audio data is valid base64 ({len(audio_bytes)} bytes)")
                        except:
                            self.print_error("Audio data is not valid base64")

                    # Print text preview
                    text = forecast.get("text", "")
                    if text:
                        preview = text[:200] + "..." if len(text) > 200 else text
                        self.print_info(f"Text preview: {preview}")

                    # Print full JSON (truncate audio for readability)
                    display_data = data.copy()
                    if "forecast" in display_data and "audio_base64" in display_data["forecast"]:
                        audio_len = len(display_data["forecast"]["audio_base64"])
                        display_data["forecast"]["audio_base64"] = f"<base64 data: {audio_len} chars>"
                    self.print_json(display_data)
                else:
                    self.print_error("Response missing forecast data")

            elif response.status_code == 404:
                self.print_info(f"No forecast found for city: {city} (404)")
                self.print_json(response.json())
            elif response.status_code == 503:
                self.print_error(f"Database unavailable (503)")
                self.print_json(response.json())
            else:
                self.print_error(f"Latest forecast endpoint returned {response.status_code}")

        except Exception as e:
            self.print_error(f"Latest forecast test failed: {e}")

    def test_forecast_history(self, city: str = "chicago", limit: int = 5, include_expired: bool = False):
        """Test GET /weather/{city}/history"""
        endpoint = f"/weather/{city}/history?limit={limit}"
        if include_expired:
            endpoint += "&include_expired=true"

        self.print_header(f"Testing Forecast History: GET {endpoint}")

        try:
            response = requests.get(f"{self.base_url}{endpoint}")

            if response.status_code == 200:
                self.print_success(f"Forecast history endpoint returned 200 OK")
                data = response.json()

                if data.get("status") == "success" and "forecasts" in data:
                    self.print_success(f"History retrieved for city: {data.get('city')}")
                    self.print_info(f"Forecast count: {data.get('count')}")

                    forecasts = data.get("forecasts", [])
                    if forecasts:
                        self.print_info(f"Showing {len(forecasts)} forecast(s):")
                        for i, fc in enumerate(forecasts[:3], 1):  # Show first 3
                            expired = fc.get("expired", False)
                            status = "EXPIRED" if expired else "VALID"
                            self.print_info(f"  {i}. {fc.get('forecast_at')} - {status} - {fc.get('language')}")
                    else:
                        self.print_info(f"No forecasts found")

                    self.print_json(data)
                else:
                    self.print_error("Response missing forecasts data")

            elif response.status_code == 503:
                self.print_error(f"Database unavailable (503)")
                self.print_json(response.json())
            else:
                self.print_error(f"Forecast history endpoint returned {response.status_code}")

        except Exception as e:
            self.print_error(f"Forecast history test failed: {e}")

    def test_nonexistent_city(self):
        """Test GET /weather/{city} with nonexistent city"""
        self.print_header("Testing Nonexistent City: GET /weather/nonexistentcity123")

        try:
            response = requests.get(f"{self.base_url}/weather/nonexistentcity123")

            if response.status_code == 404:
                self.print_success(f"Correctly returned 404 for nonexistent city")
                self.print_json(response.json())
            else:
                self.print_error(f"Expected 404 but got {response.status_code}")

        except Exception as e:
            self.print_error(f"Nonexistent city test failed: {e}")

    def test_docs_endpoint(self):
        """Test that /docs endpoint exists"""
        self.print_header("Testing API Documentation: GET /docs")

        try:
            response = requests.get(f"{self.base_url}/docs")

            if response.status_code == 200:
                self.print_success(f"API docs endpoint is accessible")
                self.print_info(f"Swagger UI available at: {self.base_url}/docs")
            else:
                self.print_error(f"Docs endpoint returned {response.status_code}")

        except Exception as e:
            self.print_error(f"Docs endpoint test failed: {e}")

    def run_all_tests(self, test_city: str = "chicago"):
        """Run all tests"""
        print(f"\n{Colors.BOLD}Weather Forecast API Test Suite{Colors.RESET}")
        print(f"{Colors.BOLD}Testing API at: {self.base_url}{Colors.RESET}")
        print(f"{Colors.BOLD}Time: {datetime.utcnow().isoformat()}Z{Colors.RESET}")

        # Test endpoints
        self.test_root_endpoint()
        self.test_health_endpoint()
        self.test_docs_endpoint()
        self.test_stats_endpoint()
        self.test_latest_forecast(test_city)
        self.test_forecast_history(test_city, limit=5, include_expired=False)
        self.test_forecast_history(test_city, limit=3, include_expired=True)
        self.test_nonexistent_city()

        # Print summary
        self.print_header("Test Summary")
        total = self.passed + self.failed
        print(f"Total tests: {total}")
        print(f"{Colors.GREEN}Passed: {self.passed}{Colors.RESET}")
        print(f"{Colors.RED}Failed: {self.failed}{Colors.RESET}")

        if self.failed == 0:
            print(f"\n{Colors.GREEN}{Colors.BOLD}All tests passed! ✓{Colors.RESET}\n")
            return 0
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}Some tests failed ✗{Colors.RESET}\n")
            return 1


def main():
    """Main entry point"""
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8080"

    tester = APITester(base_url)
    exit_code = tester.run_all_tests()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
