import time as ti
from selenium import webdriver as wbd

# NOTE:
# Use a virtual environment (venv) to avoid dependency conflicts.
# Tested on POSIX systems (Linux, macOS, BSD variants).
# Windows requires separate driver setup and PATH configuration.

# Initialize WebDriver for Chromium-based browsers.
# This works for:
# - Chromium
# - Google Chrome
# - Brave
# - Edge (Chromium-based)
# It does NOT work for Firefox (use webdriver.Firefox()).

driver = wbd.Chrome()
driver.get("https://www.amazon.com")
ti.sleep(3)
# Initialize WebDriver for Chromium-based browsers.
# This works for:
# - Chromium
# - Google Chrome
# - Brave
# - Edge (Chromium-based)
# It does NOT work for Firefox (use webdriver.Firefox()).

driver.quit()