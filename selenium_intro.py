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

#BoilerPlate to prevent the Chrome(-ium) like Browsers from closing after the program finishes
chr_opt = wbd.ChromeOptions()
chr_opt.add_experimental_option("detach" , True)

driver = wbd.Chrome(options = chr_opt)
driver.get("https://www.amazon.com")
ti.sleep(3)

#Now This is about closing the browser since we are trying to prevent quitting so these are commented out

# driver.close()  -> closes only the active tab
# driver.quit()   -> terminates entire browser session and driver process
