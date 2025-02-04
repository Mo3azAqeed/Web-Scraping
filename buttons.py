import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Initialize the WebDriver
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

def fetch_data_Agent(url):
    try:
        # Open the webpage
        driver.get(url)
        
        # Wait for the button to be clickable and click it
        wait = WebDriverWait(driver, 10)
        button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button._7c46df70.b112d6ef._4b260a84.d1c4688a._1a1c3f98._55b40d25")))
        button.click()
        
        # Wait for the dialog to appear
        dialog = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.c9a455a2.e2ce4d10")))

        # Extract the data after the button click
        agency_name = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".bc085520"))).text
        mobile_number = wait.until(EC.visibility_of_element_located((By.XPATH, "//div[@class='_05f09661']//span[@dir='ltr']"))).text
        phone_number = wait.until(EC.visibility_of_element_located((By.XPATH, "(//div[@class='_05f09661']//span[@dir='ltr'])[2]"))).text
        agent_name = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.fab2d251"))).text
        property_reference = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div._460a308e"))).text
        
        data = {
            "Agency Name": agency_name,
            "Mobile Number": mobile_number,
            "Phone Number": phone_number,
            "Agent Name": agent_name,
            "Property Reference": property_reference
        }
        
        return data
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

    finally:
        driver.quit()

# Example usage
url = "https://www.bayut.eg/en/property/details-500792989.html"  # Replace with the actual URL
data = fetch_data(url)
print(data)
