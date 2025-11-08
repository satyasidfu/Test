import asyncio

from telegram import Update

from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

import re

import os

from pathlib import Path

BOT_TOKEN = "7714074717:AAEUdT9tXgRH1v2V1ffnYEPGUGCcehkR4oM"

class NanoLinksBypasser:

    def __init__(self, update=None, context=None):
        self.update = update
        self.context = context
        self.first_redirect_url = None
        self.progress_message = None
        self.total_steps = 9
        self.current_progress = 0

    async def update_progress(self, percentage):
        """Update progress bar with actual percentage and colored rectangles"""
        if not self.update or not self.context:
            return

        try:
            self.current_progress = percentage

            # Calculate filled blocks (total 20 blocks)
            filled = int((percentage / 100) * 20)

            # Create progress bar with GREEN filled rectangles
            bar = "🟩" * filled + "⬜" * (20 - filled)

            progress_text = f"{bar}\n{percentage}%"

            if self.progress_message is None:
                # First message - send new
                msg = await self.update.message.reply_text(progress_text)
                self.progress_message = msg
            else:
                # Update existing message using correct API
                try:
                    await self.progress_message.edit_text(progress_text)
                except Exception as e:
                    pass

        except Exception as e:
            pass

    async def click_button_all_methods(self, page, search_text, button_id=None):
        """Click button using ALL possible methods"""
        try:
            # Show all buttons first
            await page.evaluate("""() => {
                const buttons = document.querySelectorAll("button");
                buttons.forEach(btn => {
                    btn.style.display = "block";
                    btn.style.visibility = "visible";
                    btn.style.pointerEvents = "auto";
                    btn.style.opacity = "1";
                    btn.disabled = false;
                });
            }""")

            # Method 1: Click by ID if provided
            if button_id:
                try:
                    element = await page.query_selector(f"#{button_id}")
                    if element:
                        await element.click()
                        return True
                except:
                    pass

            # Method 2: Find by text and click
            try:
                buttons = await page.query_selector_all("button")
                for btn in buttons:
                    text = await btn.text_content()
                    if text and search_text.upper() in text.upper():
                        await btn.scroll_into_view_if_needed()
                        await asyncio.sleep(0.5)
                        await btn.click()
                        await asyncio.sleep(2)
                        return True
            except Exception as e:
                pass

            # Method 3: JavaScript click by text
            try:
                result = await page.evaluate(f"""() => {{
                    const buttons = document.querySelectorAll("button");
                    for (let btn of buttons) {{
                        if (btn.textContent.toUpperCase().includes('{search_text.upper()}')) {{
                            btn.style.display = 'block';
                            btn.style.visibility = 'visible';
                            btn.style.pointerEvents = 'auto';
                            btn.style.opacity = '1';
                            btn.disabled = false;
                            btn.click();
                            return true;
                        }}
                    }}
                    return false;
                }}""")
                if result:
                    await asyncio.sleep(2)
                    return True
            except Exception as e:
                pass

            # Method 4: Find any link/button containing GET LINK text
            try:
                elements = await page.query_selector_all("a, button")
                for elem in elements:
                    text = await elem.text_content()
                    if text and search_text.upper() in text.upper():
                        await elem.scroll_into_view_if_needed()
                        await asyncio.sleep(0.5)
                        await elem.click()
                        await asyncio.sleep(2)
                        return True
            except Exception as e:
                pass

            return False

        except Exception as e:
            return False

    async def click_button_javascript_only(self, page, search_text):
        """Click button using JAVASCRIPT ONLY (for steps 5 & 10)"""
        try:
            result = await page.evaluate(f"""() => {{
                const buttons = document.querySelectorAll("button");
                for (let btn of buttons) {{
                    if (btn.textContent.toUpperCase().includes('{search_text.upper()}')) {{
                        btn.style.display = 'block';
                        btn.style.visibility = 'visible';
                        btn.style.pointerEvents = 'auto';
                        btn.style.opacity = '1';
                        btn.disabled = false;
                        btn.click();
                        return true;
                    }}
                }}
                return false;
            }}""")
            if result:
                await asyncio.sleep(2)
                return True
            return False
        except Exception as e:
            return False

    async def bypass_nanolinks(self, url):
        """Complete nanolinks bypass - captures FIRST redirect after GET LINK"""
        async with async_playwright() as p:
            try:
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-gpu'
                    ]
                )

                context = await browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )

                page = await context.new_page()

                # NEW: Listen for FIRST redirect after GET LINK click
                last_url = None
                redirect_listener_active = False

                async def on_frame_nav(frame):
                    """Capture FIRST redirect after GET LINK click"""
                    if frame == page.main_frame and redirect_listener_active:
                        current = page.url
                        if last_url and current != last_url and "nanolinks" not in current.lower():
                            if not self.first_redirect_url:
                                self.first_redirect_url = current

                page.on("framenavigated", on_frame_nav)

                # STEP 1: Open link
                await self.update_progress(11)
                await page.goto(url, wait_until='domcontentloaded', timeout=30000)
                await asyncio.sleep(2)

                # STEP 2: Remove popup
                await self.update_progress(22)
                try:
                    await page.evaluate("""() => {
                        const adrinoPopup = document.getElementById('adrinoPop3');
                        if (adrinoPopup) adrinoPopup.remove();
                        const adrinoElements = document.querySelectorAll('[class*="adrino"]');
                        adrinoElements.forEach(el => el.remove());
                        window.__adrinoPopMini3 = null;
                        document.body.style.overflow = 'auto';
                    }""")
                except:
                    pass

                await asyncio.sleep(1)

                # STEP 3: Click first CONTINUE (ALL METHODS)
                await self.update_progress(33)
                for i in range(30):
                    success = await self.click_button_all_methods(page, "CONTINUE")
                    if success:
                        break
                    await asyncio.sleep(1)

                # STEP 4: Scroll down
                await self.update_progress(44)
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(1)

                # STEP 5: Click "CLICK HERE TO PROCEED" (JAVASCRIPT ONLY)
                await self.update_progress(55)
                success = await self.click_button_javascript_only(page, "CLICK HERE TO PROCEED")
                await asyncio.sleep(2)

                # STEP 6: Click second CONTINUE (ALL METHODS)
                await self.update_progress(66)
                for i in range(30):
                    success = await self.click_button_all_methods(page, "CONTINUE")
                    if success:
                        break
                    await asyncio.sleep(1)

                # STEP 7: Scroll down
                await self.update_progress(77)
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(1)

                # STEP 8: Click "GET LINK" button (JAVASCRIPT ONLY) - ACTIVATE REDIRECT CAPTURE
                await self.update_progress(88)

                # Activate redirect listener
                self.first_redirect_url = None
                last_url = page.url
                redirect_listener_active = True

                for i in range(10):
                    success = await self.click_button_javascript_only(page, "GET LINK")
                    if success:
                        await asyncio.sleep(1)
                        break
                    await asyncio.sleep(1)

                # STEP 9: Wait for FIRST redirect
                for wait_idx in range(100):  # Wait up to 10 seconds
                    if self.first_redirect_url:
                        await self.update_progress(100)
                        await asyncio.sleep(2)
                        # Delete progress message
                        try:
                            await self.progress_message.delete()
                        except:
                            pass
                        await browser.close()
                        return self.first_redirect_url
                    await asyncio.sleep(0.1)

                # Fallback: return current page URL
                await self.update_progress(100)
                await asyncio.sleep(2)
                try:
                    await self.progress_message.delete()
                except:
                    pass
                final_url = page.url
                await browser.close()
                return final_url

            except Exception as e:
                await self.update.message.reply_text(f"❌ Error: {str(e)[:200]}")
                return None


# Telegram Bot Handlers

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = (
        "🤖 **NanoLinks Bypass Bot**\n\n"
        "✅ Smart progress tracking\n"
        "✅ Sends FIRST link after GET LINK\n\n"
        "Send: https://nanolinks.in/CODE"
    )
    await update.message.reply_text(welcome_message)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    if "nanolinks.in" not in user_message.lower():
        await update.message.reply_text("❌ Send valid nanolinks.in URL")
        return

    url_pattern = r'https?://(?:www\.)?nanolinks\.in/[A-Za-z0-9]+'
    urls = re.findall(url_pattern, user_message)

    if not urls:
        await update.message.reply_text("❌ No valid URL")
        return

    url = urls[0]

    try:
        bypasser = NanoLinksBypasser(update=update, context=context)
        final_url = await bypasser.bypass_nanolinks(url)

        if final_url and "nanolinks.in" not in final_url:
            await update.message.reply_text(
                f"✅ **SUCCESS!**\n\n🔗 **Link:**\n`{final_url}`"
            )
        else:
            await update.message.reply_text(f"⚠️ URL: `{final_url}`")

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)[:200]}")

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
