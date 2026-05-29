"""
Reporting & Insights Module

- Aggregates results from OrchestratorAgent
- Generates unified dashboard-style HTML reports
- Placeholders for Allure, Slack, Jira, dashboards, and alerts integration
"""

import json

class Reporting:
    def __init__(self):
        self.reports = []

    def generate_fixed_html_report(self, filename="test_report_fixed.html", no_tests_ran=False):
        """
        Generate a robust, self-contained HTML report with always-visible structure and inline CSS.
        If no_tests_ran is True, render a visible warning message.
        Otherwise, render a summary and all test results.
        """
        # Gather test results
        total_ui = total_api = total_db = 0
        passed = failed = 0
        test_sections = []

        if not no_tests_ran and self.reports:
            run = self.reports[-1]
            # UI Tests
            if "ui" in run:
                total_ui = len(run["ui"])
                ui_section = "<div class='section'><div class='section-title'>UI Tests</div><ul class='test-list'>"
                for res in run["ui"]:
                    status = "PASS" if "pass" in str(res.get("result", "")).lower() or "✅" in str(res.get("result", "")) else "FAIL"
                    color = "#22c55e" if status == "PASS" else "#dc2626"
                    if status == "PASS":
                        passed += 1
                    else:
                        failed += 1
                    ui_section += f"<li class='test-item'><span class='test-label'>Test:</span> {html_escape(res.get('test',''))}<div class='test-result' style='color:{color};'><span class='test-label'>Result:</span> {html_escape(str(res.get('result','')))}</div></li>"
                ui_section += "</ul></div>"
                test_sections.append(ui_section)
            # API Tests
            if "api" in run:
                total_api = len(run["api"])
                api_section = "<div class='section'><div class='section-title'>API Tests</div><ul class='test-list'>"
                for res in run["api"]:
                    status = "PASS" if "pass" in str(res.get("result", "")).lower() or "✅" in str(res.get("result", "")) else "FAIL"
                    color = "#22c55e" if status == "PASS" else "#dc2626"
                    if status == "PASS":
                        passed += 1
                    else:
                        failed += 1
                    api_section += f"<li class='test-item'><span class='test-label'>Test:</span> {html_escape(res.get('test',''))}<div class='test-result' style='color:{color};'><span class='test-label'>Result:</span> {html_escape(str(res.get('result','')))}</div></li>"
                api_section += "</ul></div>"
                test_sections.append(api_section)
            # DB Tests
            if "db" in run:
                total_db = len(run["db"])
                db_section = "<div class='section'><div class='section-title'>DB Tests</div><ul class='test-list'>"
                for res in run["db"]:
                    status = "PASS" if "pass" in str(res.get("result", "")).lower() or "✅" in str(res.get("result", "")) else "FAIL"
                    color = "#22c55e" if status == "PASS" else "#dc2626"
                    if status == "PASS":
                        passed += 1
                    else:
                        failed += 1
                    db_section += f"<li class='test-item'><span class='test-label'>Test:</span> {html_escape(res.get('test',''))}<div class='test-result' style='color:{color};'><span class='test-label'>Result:</span> {html_escape(str(res.get('result','')))}</div></li>"
                db_section += "</ul></div>"
                test_sections.append(db_section)

        html = [
            "<!DOCTYPE html>",
            "<html lang='en'>",
            "<head>",
            "<meta charset='UTF-8'>",
            "<meta name='viewport' content='width=device-width,initial-scale=1'>",
            "<title>Automation MCP Agent Test Report</title>",
            "<style>",
            "body { background: #f7fafc; font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 0; }",
            ".container { max-width: 1100px; margin: 32px auto; background: #fff; border-radius: 18px; box-shadow: 0 8px 32px rgba(0,0,0,0.08); padding: 32px 32px 24px 32px; }",
            ".header { display: flex; align-items: center; gap: 18px; margin-bottom: 18px; }",
            ".header .icon { font-size: 2.5rem; color: #22c55e; }",
            ".header .title { font-size: 2rem; font-weight: 800; color: #22c55e; }",
            ".summary-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 18px; margin-bottom: 28px; }",
            ".card { background: #f1f5f9; border-radius: 14px; padding: 24px 0 18px 0; text-align: center; box-shadow: 0 2px 8px rgba(34,197,94,0.04); font-weight: 700; font-size: 1.2rem; }",
            ".card.blue { color: #2563eb; background: #e0e7ff; }",
            ".card.green { color: #16a34a; background: #dcfce7; }",
            ".card.red { color: #dc2626; background: #fee2e2; }",
            ".card.yellow { color: #d97706; background: #fef9c3; }",
            ".section { margin-bottom: 24px; border-radius: 12px; padding: 18px; }",
            ".section-title { font-size: 1.1rem; font-weight: 700; margin-bottom: 10px; display: flex; align-items: center; gap: 8px; }",
            ".test-list { list-style: none; padding: 0; margin: 0; }",
            ".test-item { margin-bottom: 10px; padding: 10px 14px; border-radius: 8px; background: #fff; box-shadow: 0 1px 4px rgba(0,0,0,0.03); }",
            ".test-item .test-label { font-weight: 600; color: #334155; }",
            ".test-item .test-result { font-size: 0.98rem; color: #64748b; margin-top: 4px; }",
            ".footer { margin-top: 32px; display: flex; align-items: center; gap: 18px; }",
            ".download-btn { background: #2563eb; color: #fff; padding: 12px 28px; border-radius: 8px; font-size: 1rem; font-weight: 700; text-decoration: none; box-shadow: 0 2px 8px rgba(59,130,246,0.12); border: none; cursor: pointer; transition: background 0.2s; }",
            ".download-btn:hover { background: #1d4ed8; }",
            ".empty-message { color: #b91c1c; background: #fef2f2; border: 1.5px solid #ef4444; border-radius: 12px; padding: 24px; text-align: center; font-size: 1.2rem; margin-bottom: 24px; }",
            "</style>",
            "</head>",
            "<body>",
            "<div class='container'>",
            "<div class='header'><span class='icon'>✅</span><span class='title'>Automation Test Report</span></div>",
            "<div class='summary-grid'>",
            f"<div class='card blue'><div style='font-size:2rem'>{total_ui}</div>UI TESTS</div>",
            f"<div class='card yellow'><div style='font-size:2rem'>{total_api}</div>API TESTS</div>",
            f"<div class='card purple'><div style='font-size:2rem'>{total_db}</div>DB TESTS</div>",
            f"<div class='card green'><div style='font-size:2rem'>{passed}</div>PASSED</div>",
            f"<div class='card red'><div style='font-size:2rem'>{failed}</div>FAILED</div>",
            "</div>",
        ]
        if no_tests_ran:
            html.append("<div class='empty-message'>⚠️ No tests were executed. Please check your configuration.</div>")
        elif not test_sections:
            html.append("<div class='empty-message'>No test results found.<br>Please ensure your test suite ran and produced results.<br>If you expected results, check your test runner or reporting configuration.</div>")
        else:
            html.extend(test_sections)
        html.append("<div class='footer'><a class='download-btn' href='test_report_fixed.html' download>⬇️ Download This Report</a></div>")
        html.append("</div></body></html>")
        with open(filename, "w", encoding="utf-8") as f:
            f.write("".join(html))
        print(f"Fixed HTML report generated: {filename}")

    def add_run(self, run_results):
        self.reports.append(run_results)

    def generate_unified_report(self):
        """
        Generate a unified report from all runs.
        """
        report = {
            "total_runs": len(self.reports),
            "runs": self.reports
        }
        return json.dumps(report, indent=2)

    def send_to_allure(self, report):
        # Placeholder for Allure integration
        print("Allure integration not implemented yet.")

    def generate_html_report(self, filename="test_report.html"):
        """
        Generate a modern dashboard-style HTML report of all runs and save to a file.
        """
        # Aggregate stats
        total_browser = 0
        total_success = 0
        total_failed = 0
        total_pending = 0
        total_system = 0
        browser_success = []
        browser_failed = []
        system_passed = []
        system_failed = []

        # Only use the latest run for dashboard (like the screenshot)
        if self.reports:
            run = self.reports[-1]
            for agent, agent_results in run.items():
                for res in agent_results:
                    test = res.get('test', '')
                    result_str = str(res.get('result', ''))
                    # Heuristic for browser/system
                    is_browser = "browser" in agent.lower() or "ui" in agent.lower()
                    is_system = "sql" in agent.lower() or "api" in agent.lower() or "system" in agent.lower()
                    # Status
                    is_pass = ("✅" in result_str or "PASSED" in result_str or "rows" in result_str) and "❌" not in result_str
                    is_fail = "❌" in result_str or "FAIL" in result_str or "error" in result_str.lower()
                    # Pending: not pass or fail
                    is_pending = not is_pass and not is_fail

                    if is_browser:
                        total_browser += 1
                        if is_pass:
                            total_success += 1
                            browser_success.append((test, result_str))
                        elif is_fail:
                            total_failed += 1
                            browser_failed.append((test, result_str))
                        else:
                            total_pending += 1
                    elif is_system:
                        total_system += 1
                        if is_pass:
                            total_success += 1
                            system_passed.append((test, result_str))
                        elif is_fail:
                            total_failed += 1
                            system_failed.append((test, result_str))
                        else:
                            total_pending += 1

        total_actions = total_browser + total_system

        # HTML/CSS for dashboard
        html = [
            "<!DOCTYPE html><html lang='en'><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width,initial-scale=1'>",
            "<title>Automation MCP Agent Test Report</title>",
            "<style>",
            "body { background: #f7fafc; font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 0; }",
            ".container { max-width: 1100px; margin: 32px auto; background: #fff; border-radius: 18px; box-shadow: 0 8px 32px rgba(0,0,0,0.08); padding: 32px 32px 24px 32px; }",
            ".header { display: flex; align-items: center; gap: 18px; margin-bottom: 18px; }",
            ".header .icon { font-size: 2.5rem; color: #22c55e; }",
            ".header .title { font-size: 2rem; font-weight: 800; color: #22c55e; }",
            ".summary-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 18px; margin-bottom: 28px; }",
            ".card { background: #f1f5f9; border-radius: 14px; padding: 24px 0 18px 0; text-align: center; box-shadow: 0 2px 8px rgba(34,197,94,0.04); font-weight: 700; font-size: 1.2rem; }",
            ".card.blue { color: #2563eb; background: #e0e7ff; }",
            ".card.green { color: #16a34a; background: #dcfce7; }",
            ".card.red { color: #dc2626; background: #fee2e2; }",
            ".card.yellow { color: #d97706; background: #fef9c3; }",
            ".card.purple { color: #7c3aed; background: #ede9fe; }",
            ".section { margin-bottom: 24px; border-radius: 12px; padding: 18px; }",
            ".section.success { background: #e7fbe9; border: 1.5px solid #22c55e; }",
            ".section.fail { background: #fef2f2; border: 1.5px solid #ef4444; }",
            ".section.passed { background: #e0f2fe; border: 1.5px solid #0ea5e9; }",
            ".section-title { font-size: 1.1rem; font-weight: 700; margin-bottom: 10px; display: flex; align-items: center; gap: 8px; }",
            ".test-list { list-style: none; padding: 0; margin: 0; }",
            ".test-item { margin-bottom: 10px; padding: 10px 14px; border-radius: 8px; background: #fff; box-shadow: 0 1px 4px rgba(0,0,0,0.03); }",
            ".test-item .test-label { font-weight: 600; color: #334155; }",
            ".test-item .test-result { font-size: 0.98rem; color: #64748b; margin-top: 4px; }",
            ".footer { margin-top: 32px; display: flex; align-items: center; gap: 18px; }",
            ".download-btn { background: #2563eb; color: #fff; padding: 12px 28px; border-radius: 8px; font-size: 1rem; font-weight: 700; text-decoration: none; box-shadow: 0 2px 8px rgba(59,130,246,0.12); border: none; cursor: pointer; transition: background 0.2s; }",
            ".download-btn:hover { background: #1d4ed8; }",
            ".allure-btn { background: #16a34a; color: #fff; padding: 12px 28px; border-radius: 8px; font-size: 1rem; font-weight: 700; text-decoration: none; box-shadow: 0 2px 8px rgba(34,197,94,0.12); border: none; cursor: pointer; transition: background 0.2s; }",
            ".allure-btn:hover { background: #15803d; }",
            "</style></head><body>",
            "<div class='container'>",
            "<div class='header'><span class='icon'>✅</span><span class='title'>Automation Successfully Completed</span></div>",
            "<div class='summary-grid'>",
            f"<div class='card blue'><div style='font-size:2rem'>{total_browser}</div>BROWSER ACTIONS</div>",
            f"<div class='card green'><div style='font-size:2rem'>{total_success}</div>SUCCESSFUL</div>",
            f"<div class='card red'><div style='font-size:2rem'>{total_failed}</div>FAILED</div>",
            f"<div class='card yellow'><div style='font-size:2rem'>{total_pending}</div>PENDING</div>",
            f"<div class='card purple'><div style='font-size:2rem'>{total_system}</div>SYSTEM TESTS</div>",
            "</div>"
        ]

        # Browser Actions - Successful
        html.append("<div class='section success'><div class='section-title'><span style='font-size:1.3rem;'>🌐</span>Browser Actions - Successful (" + str(len(browser_success)) + ")</div>")
        if browser_success:
            html.append("<ul class='test-list'>")
            for test, result in browser_success:
                html.append(f"<li class='test-item'><span class='test-label'>Test:</span> {html_escape(test)}<div class='test-result'><span class='test-label'>Result:</span> {html_escape(result)}</div></li>")
            html.append("</ul>")
        else:
            html.append("<div style='color:#64748b;'>No successful browser actions.</div>")
        html.append("</div>")

        # Browser Actions - Failed
        html.append("<div class='section fail'><div class='section-title'><span style='font-size:1.3rem;'>🚫</span>Browser Actions - Failed (" + str(len(browser_failed)) + ")</div>")
        if browser_failed:
            html.append("<ul class='test-list'>")
            for test, result in browser_failed:
                html.append(f"<li class='test-item'><span class='test-label'>Test:</span> {html_escape(test)}<div class='test-result'><span class='test-label'>Result:</span> {html_escape(result)}</div></li>")
            html.append("</ul>")
        else:
            html.append("<div style='color:#64748b;'>No failed browser actions.</div>")
        html.append("</div>")

        # System Tests - Passed
        html.append("<div class='section passed'><div class='section-title'><span style='font-size:1.3rem;'>✅</span>System Tests - Passed (" + str(len(system_passed)) + ")</div>")
        if system_passed:
            html.append("<ul class='test-list'>")
            for test, result in system_passed:
                html.append(f"<li class='test-item'><span class='test-label'>Test:</span> {html_escape(test)}<div class='test-result'><span class='test-label'>Result:</span> {html_escape(result)}</div></li>")
            html.append("</ul>")
        else:
            html.append("<div style='color:#64748b;'>No passed system tests.</div>")
        html.append("</div>")

        # System Tests - Failed
        html.append("<div class='section fail'><div class='section-title'><span style='font-size:1.3rem;'>❌</span>System Tests - Failed (" + str(len(system_failed)) + ")</div>")
        if system_failed:
            html.append("<ul class='test-list'>")
            for test, result in system_failed:
                html.append(f"<li class='test-item'><span class='test-label'>Test:</span> {html_escape(test)}<div class='test-result'><span class='test-label'>Result:</span> {html_escape(result)}</div></li>")
            html.append("</ul>")
        else:
            html.append("<div style='color:#64748b;'>No failed system tests.</div>")
        html.append("</div>")

        # Footer with download and Allure buttons
        html.append("<div class='footer'>")
        html.append("<a class='download-btn' href='test_report.html' download>⬇️ Download Complete Report</a>")
        html.append("<a class='allure-btn' href='allure-report/index.html' target='_blank'>📊 View Allure Report</a>")
        html.append("</div>")

        html.append("</div></body></html>")

        with open(filename, "w", encoding="utf-8") as f:
            f.write("".join(html))
        print(f"Dashboard-style HTML report generated: {filename}")

    def send_to_slack(self, report, slack_token=None, channel="#general"):
        """
        Send report to Slack using slack_sdk.
        Requires: pip install slack_sdk
        """
        try:
            from slack_sdk import WebClient
            from slack_sdk.errors import SlackApiError
        except ImportError:
            print("slack_sdk not installed. Run: pip install slack_sdk")
            return
        if not slack_token:
            slack_token = os.getenv("SLACK_BOT_TOKEN")
        if not slack_token:
            print("Slack token not provided or set in environment.")
            return
        client = WebClient(token=slack_token)
        try:
            response = client.chat_postMessage(
                channel=channel,
                text=f"Automation MCP Agent Report:\n```{report}```"
            )
            print(f"Slack message sent: {response['ts']}")
        except SlackApiError as e:
            print(f"Slack API error: {e.response['error']}")

    def send_to_jira(self, report, jira_url=None, jira_user=None, jira_token=None, project_key="AGENT"):
        """
        Create a Jira issue with the report.
        Requires: pip install jira
        """
        try:
            from jira import JIRA
        except ImportError:
            print("jira not installed. Run: pip install jira")
            return
        jira_url = jira_url or os.getenv("JIRA_URL")
        jira_user = jira_user or os.getenv("JIRA_USER")
        jira_token = jira_token or os.getenv("JIRA_TOKEN")
        if not all([jira_url, jira_user, jira_token]):
            print("Jira credentials not provided or set in environment.")
            return
        jira = JIRA(server=jira_url, basic_auth=(jira_user, jira_token))
        issue_dict = {
            'project': {'key': project_key},
            'summary': 'Automation MCP Agent Report',
            'description': report,
            'issuetype': {'name': 'Task'},
        }
        issue = jira.create_issue(fields=issue_dict)
        print(f"Jira issue created: {issue.key}")

    def alert_dashboard(self, report):
        """Send alert to dashboard/monitoring system (stub)."""
        # TODO: Integrate with dashboard/alerting (e.g., Grafana, Prometheus Alertmanager)
        print("Dashboard/alert integration not implemented yet.")

def html_escape(text):
    import html
    return html.escape(text)
