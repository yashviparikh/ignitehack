#!/usr/bin/env python3
"""
Quick Testing (qt.py) - Hackathon Template Health Checker
========================================================

Comprehensive automated testing for all hackathon templates and presets.
Ensures all components are working properly without external dependencies.

Usage: python qt.py
"""

import os
import sys
import json
import time
import subprocess
import importlib.util
from pathlib import Path
from typing import Dict, List, Tuple, Any
from datetime import datetime

# ANSI Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

class QuickTester:
    """Comprehensive testing suite for hackathon templates."""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.results = {
            "test_time": datetime.now().isoformat(),
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "tests": []
        }
        self.current_test = ""
    
    def log(self, message: str, level: str = "INFO", color: str = Colors.WHITE):
        """Enhanced logging with colors and formatting."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = f"[{timestamp}] {level.upper()}"
        print(f"{color}{prefix}: {message}{Colors.END}")
    
    def test_result(self, test_name: str, passed: bool, message: str = "", details: Any = None):
        """Record test result with detailed information."""
        self.results["total_tests"] += 1
        
        if passed:
            self.results["passed"] += 1
            status = "PASS"
            color = Colors.GREEN
            icon = "✅"
        else:
            self.results["failed"] += 1
            status = "FAIL"
            color = Colors.RED
            icon = "❌"
        
        self.results["tests"].append({
            "name": test_name,
            "status": status,
            "message": message,
            "details": details
        })
        
        self.log(f"{icon} {test_name}: {status} - {message}", color=color)
    
    def skip_test(self, test_name: str, reason: str):
        """Mark test as skipped."""
        self.results["total_tests"] += 1
        self.results["skipped"] += 1
        self.results["tests"].append({
            "name": test_name,
            "status": "SKIP",
            "message": reason,
            "details": None
        })
        self.log(f"⏭️  {test_name}: SKIPPED - {reason}", color=Colors.YELLOW)

class TemplateHealthChecker(QuickTester):
    """Health checker for all hackathon templates."""
    
    def run_all_tests(self):
        """Run comprehensive test suite."""
        self.log("🚀 Starting Hackathon Template Health Check", color=Colors.CYAN + Colors.BOLD)
        self.log("=" * 60, color=Colors.CYAN)
        
        # Test template structure
        self.test_template_structure()
        
        # Test Express.js template
        self.test_express_template()
        
        # Test FastAPI template
        self.test_fastapi_template()
        
        # Test shared components
        self.test_shared_components()
        
        # Test configuration files
        self.test_configuration_files()
        
        # Test documentation
        self.test_documentation()
        
        # Generate final report
        self.generate_report()
    
    def test_template_structure(self):
        """Test overall template directory structure."""
        self.log("📁 Testing Template Structure", color=Colors.BLUE + Colors.BOLD)
        
        # Check main directories
        templates_dir = self.base_path / "templates"
        expected_dirs = ["express-api", "fastapi-cloud"]
        
        if templates_dir.exists():
            self.test_result("Templates Directory", True, "Templates directory exists")
            
            for template_dir in expected_dirs:
                dir_path = templates_dir / template_dir
                if dir_path.exists():
                    self.test_result(f"Template: {template_dir}", True, f"Directory exists at {dir_path}")
                else:
                    self.test_result(f"Template: {template_dir}", False, f"Directory missing at {dir_path}")
        else:
            self.test_result("Templates Directory", False, "Templates directory not found")
        
        # Check shared directory
        shared_dir = self.base_path / "shared"
        if shared_dir.exists():
            self.test_result("Shared Components", True, "Shared directory exists")
        else:
            self.test_result("Shared Components", False, "Shared directory missing")
    
    def test_express_template(self):
        """Test Express.js template components."""
        self.log("🟢 Testing Express.js Template", color=Colors.GREEN + Colors.BOLD)
        
        express_dir = self.base_path / "templates" / "express-api"
        
        if not express_dir.exists():
            self.skip_test("Express Template", "Directory not found")
            return
        
        # Test essential files
        essential_files = [
            "package.json",
            "server.js",
            "README.md",
            "Dockerfile",
            ".env.example"
        ]
        
        for file_name in essential_files:
            file_path = express_dir / file_name
            if file_path.exists():
                self.test_result(f"Express: {file_name}", True, f"File exists")
                
                # Test package.json content
                if file_name == "package.json":
                    try:
                        with open(file_path, 'r') as f:
                            package_data = json.load(f)
                        
                        if "express" in package_data.get("dependencies", {}):
                            self.test_result("Express: Dependencies", True, "Express dependency found")
                        else:
                            self.test_result("Express: Dependencies", False, "Express dependency missing")
                            
                        if "scripts" in package_data:
                            self.test_result("Express: Scripts", True, f"Found {len(package_data['scripts'])} scripts")
                        else:
                            self.test_result("Express: Scripts", False, "No scripts found")
                            
                    except Exception as e:
                        self.test_result("Express: package.json", False, f"Invalid JSON: {e}")
            else:
                self.test_result(f"Express: {file_name}", False, f"File missing")
        
        # Test directory structure
        expected_dirs = ["middleware", "routes", "config", "utils"]
        for dir_name in expected_dirs:
            dir_path = express_dir / dir_name
            if dir_path.exists():
                file_count = len(list(dir_path.glob("*.js")))
                self.test_result(f"Express: {dir_name}/", True, f"Directory exists with {file_count} JS files")
            else:
                self.test_result(f"Express: {dir_name}/", False, "Directory missing")
    
    def test_fastapi_template(self):
        """Test FastAPI template components."""
        self.log("🐍 Testing FastAPI Template", color=Colors.MAGENTA + Colors.BOLD)
        
        fastapi_dir = self.base_path / "templates" / "fastapi-cloud"
        
        if not fastapi_dir.exists():
            self.skip_test("FastAPI Template", "Directory not found")
            return
        
        # Test essential files
        essential_files = [
            "requirements.txt",
            "requirements-dev.txt",
            "main.py",
            "README.md",
            "Dockerfile",
            ".env.example"
        ]
        
        for file_name in essential_files:
            file_path = fastapi_dir / file_name
            if file_path.exists():
                self.test_result(f"FastAPI: {file_name}", True, "File exists")
                
                # Test requirements content
                if "requirements" in file_name:
                    try:
                        with open(file_path, 'r') as f:
                            content = f.read()
                        
                        required_packages = ["fastapi", "uvicorn", "pydantic"]
                        found_packages = [pkg for pkg in required_packages if pkg in content.lower()]
                        
                        if len(found_packages) == len(required_packages):
                            self.test_result(f"FastAPI: {file_name} deps", True, f"All required packages found")
                        else:
                            missing = set(required_packages) - set(found_packages)
                            self.test_result(f"FastAPI: {file_name} deps", False, f"Missing: {missing}")
                            
                    except Exception as e:
                        self.test_result(f"FastAPI: {file_name}", False, f"Read error: {e}")
            else:
                self.test_result(f"FastAPI: {file_name}", False, "File missing")
        
        # Test Python module structure
        app_dir = fastapi_dir / "app"
        if app_dir.exists():
            self.test_result("FastAPI: app/ module", True, "App module directory exists")
            
            # Test submodules
            expected_modules = ["config.py", "routers", "middleware", "models"]
            for module in expected_modules:
                module_path = app_dir / module
                if module_path.exists():
                    if module_path.is_file():
                        self.test_result(f"FastAPI: app/{module}", True, "Module file exists")
                    else:
                        py_files = len(list(module_path.glob("*.py")))
                        self.test_result(f"FastAPI: app/{module}/", True, f"Module directory with {py_files} files")
                else:
                    self.test_result(f"FastAPI: app/{module}", False, "Module missing")
        else:
            self.test_result("FastAPI: app/ module", False, "App module directory missing")
        
        # Test FastAPI app creation
        self.test_fastapi_app_creation(fastapi_dir)
    
    def test_fastapi_app_creation(self, fastapi_dir: Path):
        """Test if FastAPI app can be created without errors."""
        try:
            # Change to FastAPI directory
            original_cwd = os.getcwd()
            os.chdir(fastapi_dir)
            
            # Add current directory to Python path
            sys.path.insert(0, str(fastapi_dir))
            
            # Try to import and create the app
            spec = importlib.util.spec_from_file_location("main", fastapi_dir / "main.py")
            main_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(main_module)
            
            # Create the app
            app = main_module.create_app()
            
            if hasattr(app, 'title') and hasattr(app, 'version'):
                self.test_result("FastAPI: App Creation", True, f"App created: {app.title} v{app.version}")
                
                # Test app routes
                routes = [route.path for route in app.routes]
                essential_routes = ["/", "/health"]
                found_routes = [route for route in essential_routes if route in routes]
                
                if len(found_routes) == len(essential_routes):
                    self.test_result("FastAPI: Essential Routes", True, f"All routes found: {found_routes}")
                else:
                    missing = set(essential_routes) - set(found_routes)
                    self.test_result("FastAPI: Essential Routes", False, f"Missing routes: {missing}")
            else:
                self.test_result("FastAPI: App Creation", False, "Invalid app object")
                
        except Exception as e:
            self.test_result("FastAPI: App Creation", False, f"Import/creation failed: {str(e)}")
        finally:
            # Restore original working directory
            os.chdir(original_cwd)
            # Remove from path
            if str(fastapi_dir) in sys.path:
                sys.path.remove(str(fastapi_dir))
    
    def test_shared_components(self):
        """Test shared components and configurations."""
        self.log("🔗 Testing Shared Components", color=Colors.CYAN + Colors.BOLD)
        
        shared_dir = self.base_path / "shared"
        
        if not shared_dir.exists():
            self.skip_test("Shared Components", "Shared directory not found")
            return
        
        # Test configuration files
        config_dir = shared_dir / "configs"
        if config_dir.exists():
            self.test_result("Shared: configs/", True, "Config directory exists")
            
            config_files = list(config_dir.glob("*.js")) + list(config_dir.glob("*.json"))
            if config_files:
                self.test_result("Shared: Config Files", True, f"Found {len(config_files)} config files")
                
                # Test security config specifically
                security_config = config_dir / "security.js"
                if security_config.exists():
                    self.test_result("Shared: Security Config", True, "Security configuration exists")
                else:
                    self.test_result("Shared: Security Config", False, "Security configuration missing")
            else:
                self.test_result("Shared: Config Files", False, "No config files found")
        else:
            self.test_result("Shared: configs/", False, "Config directory missing")
        
        # Test Docker files
        docker_dir = shared_dir / "docker"
        if docker_dir.exists():
            docker_files = list(docker_dir.glob("*.yml")) + list(docker_dir.glob("*.yaml"))
            self.test_result("Shared: Docker", True, f"Docker directory with {len(docker_files)} files")
        else:
            self.test_result("Shared: Docker", False, "Docker directory missing")
    
    def test_configuration_files(self):
        """Test various configuration files."""
        self.log("⚙️ Testing Configuration Files", color=Colors.YELLOW + Colors.BOLD)
        
        # Test root configuration files
        config_files = [
            ".gitignore",
            "README.md"
        ]
        
        for config_file in config_files:
            file_path = self.base_path / config_file
            if file_path.exists():
                file_size = file_path.stat().st_size
                self.test_result(f"Config: {config_file}", True, f"Exists ({file_size} bytes)")
            else:
                self.test_result(f"Config: {config_file}", False, "File missing")
        
        # Test .env.example files
        for template in ["express-api", "fastapi-cloud"]:
            env_file = self.base_path / "templates" / template / ".env.example"
            if env_file.exists():
                try:
                    with open(env_file, 'r') as f:
                        content = f.read()
                    
                    # Count environment variables
                    env_vars = [line for line in content.split('\n') if '=' in line and not line.strip().startswith('#')]
                    self.test_result(f"Config: {template}/.env.example", True, f"{len(env_vars)} environment variables")
                except Exception as e:
                    self.test_result(f"Config: {template}/.env.example", False, f"Read error: {e}")
            else:
                self.test_result(f"Config: {template}/.env.example", False, "Environment file missing")
    
    def test_documentation(self):
        """Test documentation files and completeness."""
        self.log("📚 Testing Documentation", color=Colors.WHITE + Colors.BOLD)
        
        # Test main README
        main_readme = self.base_path / "README.md"
        if main_readme.exists():
            try:
                with open(main_readme, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for essential sections
                essential_sections = ["installation", "usage", "template", "feature"]
                found_sections = [section for section in essential_sections 
                                if section.lower() in content.lower()]
                
                self.test_result("Docs: Main README", True, 
                               f"Found {len(found_sections)}/{len(essential_sections)} sections")
                
                # Check word count
                word_count = len(content.split())
                if word_count > 100:
                    self.test_result("Docs: README Content", True, f"{word_count} words")
                else:
                    self.test_result("Docs: README Content", False, f"Too short: {word_count} words")
                    
            except Exception as e:
                self.test_result("Docs: Main README", False, f"Read error: {e}")
        else:
            self.test_result("Docs: Main README", False, "Main README missing")
        
        # Test template-specific READMEs
        for template in ["express-api", "fastapi-cloud"]:
            readme_path = self.base_path / "templates" / template / "README.md"
            if readme_path.exists():
                try:
                    with open(readme_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    word_count = len(content.split())
                    self.test_result(f"Docs: {template} README", True, f"{word_count} words")
                except Exception as e:
                    self.test_result(f"Docs: {template} README", False, f"Read error: {e}")
            else:
                self.test_result(f"Docs: {template} README", False, "Template README missing")
    
    def generate_report(self):
        """Generate comprehensive test report."""
        self.log("📊 Generating Test Report", color=Colors.BLUE + Colors.BOLD)
        print()
        
        # Summary statistics
        total = self.results["total_tests"]
        passed = self.results["passed"]
        failed = self.results["failed"]
        skipped = self.results["skipped"]
        
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        # Print summary box
        print(f"{Colors.BOLD}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}        HACKATHON TEMPLATE HEALTH CHECK REPORT{Colors.END}")
        print(f"{Colors.BOLD}{'='*60}{Colors.END}")
        print()
        
        print(f"{Colors.BOLD}📈 TEST SUMMARY:{Colors.END}")
        print(f"   🟢 Passed:  {passed:3d} tests")
        print(f"   🔴 Failed:  {failed:3d} tests")
        print(f"   🟡 Skipped: {skipped:3d} tests")
        print(f"   📊 Total:   {total:3d} tests")
        print(f"   💯 Success Rate: {pass_rate:.1f}%")
        print()
        
        # Status indicator
        if pass_rate >= 90:
            status_color = Colors.GREEN
            status_icon = "🎉"
            status_text = "EXCELLENT"
        elif pass_rate >= 75:
            status_color = Colors.YELLOW
            status_icon = "✅"
            status_text = "GOOD"
        elif pass_rate >= 50:
            status_color = Colors.YELLOW
            status_icon = "⚠️"
            status_text = "NEEDS ATTENTION"
        else:
            status_color = Colors.RED
            status_icon = "❌"
            status_text = "CRITICAL ISSUES"
        
        print(f"{Colors.BOLD}🏆 OVERALL STATUS:{Colors.END}")
        print(f"   {status_color}{status_icon} {status_text} ({pass_rate:.1f}% success rate){Colors.END}")
        print()
        
        # Failed tests details
        if failed > 0:
            print(f"{Colors.BOLD}{Colors.RED}❌ FAILED TESTS:{Colors.END}")
            for test in self.results["tests"]:
                if test["status"] == "FAIL":
                    print(f"   • {test['name']}: {test['message']}")
            print()
        
        # Recommendations
        print(f"{Colors.BOLD}💡 RECOMMENDATIONS:{Colors.END}")
        if pass_rate >= 90:
            print("   🎯 Templates are ready for hackathon use!")
            print("   🚀 Consider adding more advanced features")
        elif failed > 0:
            print("   🔧 Fix failed tests before using templates")
            print("   📖 Check documentation for setup instructions")
        
        if skipped > 0:
            print("   📝 Some tests were skipped - consider implementing missing components")
        
        print()
        print(f"{Colors.BOLD}{'='*60}{Colors.END}")
        
        # Save detailed report
        report_file = self.base_path / "test_report.json"
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        self.log(f"Detailed report saved to: {report_file}", color=Colors.CYAN)
        
        return pass_rate >= 75  # Return success if 75% or higher pass rate

def main():
    """Main entry point for quick testing."""
    print(f"{Colors.BOLD}{Colors.CYAN}")
    print("██╗  ██╗ █████╗  ██████╗██╗  ██╗ █████╗ ████████╗██╗  ██╗ ██████╗ ███╗   ██╗")
    print("██║  ██║██╔══██╗██╔════╝██║ ██╔╝██╔══██╗╚══██╔══╝██║  ██║██╔═══██╗████╗  ██║")
    print("███████║███████║██║     █████╔╝ ███████║   ██║   ███████║██║   ██║██╔██╗ ██║")
    print("██╔══██║██╔══██║██║     ██╔═██╗ ██╔══██║   ██║   ██╔══██║██║   ██║██║╚██╗██║")
    print("██║  ██║██║  ██║╚██████╗██║  ██╗██║  ██║   ██║   ██║  ██║╚██████╔╝██║ ╚████║")
    print("╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝")
    print("                           TEMPLATE HEALTH CHECKER")
    print(f"{Colors.END}")
    print()
    
    # Run tests
    checker = TemplateHealthChecker()
    success = checker.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
