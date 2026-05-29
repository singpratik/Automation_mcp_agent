#!/usr/bin/env python3
"""
Debug script for TTS monitoring on VMock pages
Run this while on a VMock interview page to see what's detected
"""

import asyncio
import re
from playwright.async_api import async_playwright

async def debug_vmock_page(url: str = None):
    """Debug what elements are found on a VMock page"""
    
    async with async_playwright() as p:
        # Connect to existing Chrome instance on debugging port 9222
        try:
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
            print("✅ Connected to Chrome debugging port 9222")
        except Exception as e:
            print(f"❌ Failed to connect to Chrome: {e}")
            print("Make sure Chrome is running with --remote-debugging-port=9222")
            return
        
        contexts = browser.contexts
        if not contexts:
            print("❌ No browser contexts found")
            return
        
        context = contexts[0]
        pages = context.pages
        
        if not pages:
            print("❌ No pages found")
            return
        
        # Use first page or find VMock page
        page = pages[0]
        for p in pages:
            if 'vmock' in p.url.lower():
                page = p
                break
        
        current_url = page.url
        print(f"\n📄 Current URL: {current_url}")
        
        if 'vmock' not in current_url.lower():
            print("⚠️  Not on a VMock domain!")
            print("\nNavigate to a VMock interview page first, then run this script again.")
            return
        
        print("\n" + "="*80)
        print("CHECKING QUESTION SELECTORS")
        print("="*80)
        
        # Test all selectors
        question_selectors = [
            ('Regex: Q.|Question', 'text=/^Q\\.|Question/i'),
            ('Regex: Please tell', 'text=/Please tell/i'),
            ('Regex: Describe', 'text=/Describe/i'),
            ('Regex: What.*about', 'text=/What.*about/i'),
            ('Regex: Tell me about', 'text=/Tell me about/i'),
            ('Class: question', '[class*="question"]'),
            ('Data: question', '[data-testid*="question"]')
        ]
        
        found_any = False
        for name, selector in question_selectors:
            try:
                elements = await page.locator(selector).all()
                if elements:
                    print(f"\n✅ {name}: Found {len(elements)} element(s)")
                    for i, elem in enumerate(elements[:3]):  # Show first 3
                        try:
                            text = await elem.text_content()
                            text_preview = (text or '').strip()[:150]
                            print(f"   [{i+1}] {text_preview}...")
                            found_any = True
                        except:
                            pass
                else:
                    print(f"❌ {name}: No elements found")
            except Exception as e:
                print(f"❌ {name}: Error - {e}")
        
        print("\n" + "="*80)
        print("CHECKING BODY TEXT FALLBACK")
        print("="*80)
        
        try:
            body_text = await page.locator("body").inner_text(timeout=5000)
            body_text = re.sub(r'\s+', ' ', body_text or '').strip()
            
            print(f"📝 Body text length: {len(body_text)} characters")
            print(f"📝 First 500 chars: {body_text[:500]}...")
            
            fallback_patterns = [
                ('please tell me about yourself', r'(please tell me about yourself[^.?!]{0,250}[.?!]?)'),
                ('tell me about yourself', r'(tell me about yourself[^.?!]{0,250}[.?!]?)'),
                ('describe your experience', r'(describe your experience[^.?!]{0,250}[.?!]?)'),
                ('what can you tell us', r'(what can you tell us about[^.?!]{0,250}[.?!]?)'),
                ('Q.|question pattern', r'((?:q\.?|question)\s*[:\-]?\s*[^.?!]{10,250}[.?!]?)'),
            ]
            
            print("\nTesting fallback regex patterns:")
            for name, pattern in fallback_patterns:
                match = re.search(pattern, body_text, re.IGNORECASE)
                if match:
                    question = match.group(1).strip()
                    print(f"✅ {name}: FOUND!")
                    print(f"   Text: {question[:200]}...")
                    found_any = True
                else:
                    print(f"❌ {name}: Not found")
                    
        except Exception as e:
            print(f"❌ Error reading body text: {e}")
        
        print("\n" + "="*80)
        print("PAGE STRUCTURE ANALYSIS")
        print("="*80)
        
        # Check for common VMock elements
        try:
            # Check for video elements
            video_elements = await page.locator("video").count()
            print(f"📹 Video elements: {video_elements}")
            
            # Check for any text containing "question"
            question_text_elements = await page.locator("text=/question/i").count()
            print(f"💬 Elements with 'question' text: {question_text_elements}")
            
            # Check for headers
            h1_count = await page.locator("h1").count()
            h2_count = await page.locator("h2").count()
            h3_count = await page.locator("h3").count()
            print(f"📋 Headers: h1={h1_count}, h2={h2_count}, h3={h3_count}")
            
            # Sample h1-h3 text
            for tag in ["h1", "h2", "h3"]:
                elements = await page.locator(tag).all()
                if elements:
                    print(f"\n{tag.upper()} text samples:")
                    for i, elem in enumerate(elements[:3]):
                        try:
                            text = await elem.text_content()
                            print(f"   {text.strip()[:100]}")
                        except:
                            pass
                            
        except Exception as e:
            print(f"Error analyzing page structure: {e}")
        
        if not found_any:
            print("\n" + "="*80)
            print("⚠️  NO QUESTIONS DETECTED!")
            print("="*80)
            print("\nPossible reasons:")
            print("1. Not on the actual interview question page yet")
            print("2. Page is still loading")
            print("3. VMock changed their HTML structure")
            print("4. Questions are in an iframe")
            print("\nNext steps:")
            print("- Make sure you're on the actual question screen")
            print("- Check browser console for any errors")
            print("- Try refreshing the page")
        
        print("\n✅ Debug complete!")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_vmock_page())
