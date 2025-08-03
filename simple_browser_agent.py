import asyncio
import os
from playwright.async_api import async_playwright
import logging

class SimpleBrowserAgent:
    def __init__(self, enable_media_permissions=False, y4m_file_path=None):
        self.enable_media_permissions = enable_media_permissions
        self.y4m_file_path = y4m_file_path
        self.browser = None
        self.page = None
        self.logs = []
        
    def log(self, message):
        """Add log message"""
        self.logs.append(message)
        print(f"[BROWSER] {message}")
    
    async def start_browser(self):
        """Start the browser"""
        try:
            self.log("🚀 Starting browser...")
            
            playwright = await async_playwright().start()
            
            # Browser arguments
            args = [
                "--no-first-run",
                "--disable-extensions",
                "--disable-default-apps"
            ]
            
            # Add Y4M file for fake camera if provided
            if self.y4m_file_path and os.path.exists(self.y4m_file_path):
                args.extend([
                    "--use-fake-ui-for-media-stream",
                    "--use-fake-device-for-media-stream",
                    f"--use-file-for-fake-video-capture={self.y4m_file_path}"
                ])
                self.log(f"✅ Y4M file configured: {self.y4m_file_path}")
            
            # Launch browser
            self.browser = await playwright.chromium.launch(
                headless=False,
                args=args
            )
            
            # Create context and page
            context = await self.browser.new_context()
            self.page = await context.new_page()
            
            self.log("✅ Browser started successfully")
            return True
            
        except Exception as e:
            self.log(f"❌ Failed to start browser: {str(e)}")
            return False
    
    async def vmock_login_automation(self, email, password):
        """Automate VMock login process"""
        try:
            if not self.page:
                if not await self.start_browser():
                    return "Failed to start browser"
            
            # Step 1: Go to VMock login page
            self.log("🌐 Navigating to VMock login page...")
            await self.page.goto("https://www.vmock.com/login", wait_until="networkidle")
            await asyncio.sleep(2)
            
            # Step 2: Click on Login button
            self.log("🔘 Looking for Login button...")
            try:
                login_button = await self.page.wait_for_selector("text=Login", timeout=10000)
                await login_button.click()
                await asyncio.sleep(2)
                self.log("✅ Clicked Login button")
            except:
                self.log("⚠️ Login button not found, continuing...")
            
            # Step 3: Select "Login with Email"
            self.log("📧 Looking for 'Login with Email' option...")
            try:
                email_login = await self.page.wait_for_selector("text=Login with Email", timeout=10000)
                await email_login.click()
                await asyncio.sleep(2)
                self.log("✅ Selected 'Login with Email'")
            except:
                self.log("⚠️ 'Login with Email' not found, looking for email field directly...")
            
            # Step 4: Enter email
            self.log(f"✉️ Entering email: {email}")
            try:
                # Try different selectors for email field
                email_selectors = [
                    'input[type="email"]',
                    'input[name="email"]',
                    'input[placeholder*="email" i]',
                    '#email',
                    '.email'
                ]
                
                email_field = None
                for selector in email_selectors:
                    try:
                        email_field = await self.page.wait_for_selector(selector, timeout=5000)
                        break
                    except:
                        continue
                
                if email_field:
                    await email_field.fill(email)
                    self.log("✅ Email entered successfully")
                else:
                    self.log("❌ Email field not found")
                    return "Email field not found"
                    
            except Exception as e:
                self.log(f"❌ Failed to enter email: {str(e)}")
                return f"Failed to enter email: {str(e)}"
            
            # Step 5: Enter password
            self.log("🔒 Entering password...")
            try:
                password_selectors = [
                    'input[type="password"]',
                    'input[name="password"]',
                    '#password',
                    '.password'
                ]
                
                password_field = None
                for selector in password_selectors:
                    try:
                        password_field = await self.page.wait_for_selector(selector, timeout=5000)
                        break
                    except:
                        continue
                
                if password_field:
                    await password_field.fill(password)
                    self.log("✅ Password entered successfully")
                else:
                    self.log("❌ Password field not found")
                    return "Password field not found"
                    
            except Exception as e:
                self.log(f"❌ Failed to enter password: {str(e)}")
                return f"Failed to enter password: {str(e)}"
            
            # Step 6: Click Login button
            self.log("🔐 Clicking Login button...")
            try:
                login_submit_selectors = [
                    'button[type="submit"]',
                    'input[type="submit"]',
                    'button:has-text("Login")',
                    'button:has-text("Sign In")',
                    '.login-button',
                    '#login-button'
                ]
                
                login_submit = None
                for selector in login_submit_selectors:
                    try:
                        login_submit = await self.page.wait_for_selector(selector, timeout=5000)
                        break
                    except:
                        continue
                
                if login_submit:
                    await login_submit.click()
                    self.log("✅ Clicked Login button")
                    await asyncio.sleep(5)  # Wait for login to process
                else:
                    self.log("❌ Login submit button not found")
                    return "Login submit button not found"
                    
            except Exception as e:
                self.log(f"❌ Failed to click login: {str(e)}")
                return f"Failed to click login: {str(e)}"
            
            # Step 7: Wait for dashboard
            self.log("⏳ Waiting for dashboard to load...")
            await asyncio.sleep(5)
            
            # Step 8: Click on Interview tab
            self.log("🎤 Looking for Interview tab...")
            try:
                interview_selectors = [
                    'text=Interview',
                    '[href*="interview"]',
                    'a:has-text("Interview")',
                    '.interview-tab'
                ]
                
                interview_tab = None
                for selector in interview_selectors:
                    try:
                        interview_tab = await self.page.wait_for_selector(selector, timeout=10000)
                        break
                    except:
                        continue
                
                if interview_tab:
                    await interview_tab.click()
                    self.log("✅ Clicked Interview tab")
                    await asyncio.sleep(3)
                else:
                    self.log("❌ Interview tab not found")
                    return "Interview tab not found"
                    
            except Exception as e:
                self.log(f"❌ Failed to click Interview tab: {str(e)}")
                return f"Failed to click Interview tab: {str(e)}"
            
            # Step 9: Click on EP
            self.log("📝 Looking for EP option...")
            try:
                ep_selectors = [
                    'text=EP',
                    '[href*="ep"]',
                    'a:has-text("EP")',
                    '.ep-option'
                ]
                
                ep_option = None
                for selector in ep_selectors:
                    try:
                        ep_option = await self.page.wait_for_selector(selector, timeout=10000)
                        break
                    except:
                        continue
                
                if ep_option:
                    await ep_option.click()
                    self.log("✅ Clicked EP option")
                    await asyncio.sleep(3)
                else:
                    self.log("❌ EP option not found")
                    return "EP option not found"
                    
            except Exception as e:
                self.log(f"❌ Failed to click EP: {str(e)}")
                return f"Failed to click EP: {str(e)}"
            
            # Step 10: Click Start Interview button
            self.log("▶️ Looking for Start Interview button...")
            try:
                start_selectors = [
                    'text=Start Interview',
                    'button:has-text("Start")',
                    '[href*="start"]',
                    '.start-interview'
                ]
                
                start_button = None
                for selector in start_selectors:
                    try:
                        start_button = await self.page.wait_for_selector(selector, timeout=10000)
                        break
                    except:
                        continue
                
                if start_button:
                    await start_button.click()
                    self.log("✅ Clicked Start Interview button")
                    await asyncio.sleep(5)
                else:
                    self.log("❌ Start Interview button not found")
                    return "Start Interview button not found"
                    
            except Exception as e:
                self.log(f"❌ Failed to click Start Interview: {str(e)}")
                return f"Failed to click Start Interview: {str(e)}"
            
            self.log("🎉 VMock login automation completed successfully!")
            return "✅ Successfully completed VMock login and started interview"
            
        except Exception as e:
            self.log(f"❌ VMock automation failed: {str(e)}")
            return f"VMock automation failed: {str(e)}"
    
    async def close(self):
        """Close the browser"""
        try:
            if self.browser:
                await self.browser.close()
                self.log("🔒 Browser closed")
        except Exception as e:
            self.log(f"⚠️ Error closing browser: {str(e)}")
    
    def get_logs(self):
        """Get all logs"""
        return self.logs.copy()

# Synchronous wrapper for Streamlit
def run_vmock_automation(email, password, y4m_file_path=None):
    """Run VMock automation synchronously"""
    async def _run():
        agent = SimpleBrowserAgent(
            enable_media_permissions=True,
            y4m_file_path=y4m_file_path
        )
        
        try:
            result = await agent.vmock_login_automation(email, password)
            logs = agent.get_logs()
            
            # Keep browser open for manual verification
            input("\n⏸️  Press Enter to close browser...")
            await agent.close()
            
            return result, logs
            
        except Exception as e:
            await agent.close()
            return f"Error: {str(e)}", agent.get_logs()
    
    return asyncio.run(_run())