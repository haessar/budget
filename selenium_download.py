import string
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from config import chromedriver_path, transactions_dir

def cred_getter(acc):
    """Open credentials from secure location."""
    from creds import natwest
    return natwest[acc]

class NatWestExport(webdriver.Chrome):
    multiplier = 0
    def __init__(self, *args, **kwargs):
        chrome_options = webdriver.ChromeOptions()
        prefs = {
            'download.default_directory': transactions_dir,
            'directory_upgrade': True,
        }
        chrome_options.add_experimental_option('prefs', prefs)
        kwargs['chrome_options'] = chrome_options
        super(self.__class__, self).__init__(chromedriver_path, *args, **kwargs)
    def __enter__(self):
        self.get('https://www.nwolb.com/Login.aspx')
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.quit()
    def close_popup(self):
        try:
            self.find_element_by_id('splash-28021-close-button').click()
        except Exception:
            pass
    def login(self):
        self.switch_to.frame(self.find_element(By.XPATH, '//frame[@id="ctl00_secframe"]'))
        self.close_popup()
        self.find_element(By.XPATH, '//*[@id="ctl00_mainContent_LI5TABA_DBID_edit"]').send_keys(cred_getter('cust'))
        # TODO Maintenance carried out 2:00 - 2:40 (local time) every night. Add in check for this.
        self.find_element(By.XPATH, '//*[@id="ctl00_mainContent_LI5TABA_LI5-LBA_button_button"]').click()
        time.sleep(1 * self.multiplier)
        for letter in list(string.ascii_uppercase)[:6]:
            cred_type = 'pin' if letter in ['A', 'B', 'C'] else 'passw'
            pin = (
                self.find_element(By.XPATH, '//*[@id="ctl00_mainContent_Tab1_LI6DDAL%sLabel"]' % letter)
                    .get_attribute('innerHTML')
            )
            pin = int(''.join([str(s) for s in list(pin) if s.isdigit()]))
            (
                self.find_element(By.XPATH, '//*[@id="ctl00_mainContent_Tab1_LI6PPE%s_edit"]' % letter)
                    .send_keys(str(cred_getter(cred_type))[pin - 1])
            )
        self.find_element(By.XPATH, '//*[@id="ctl00_mainContent_Tab1_next_text_button_button"]').click()
    def export_transactions(self):
        # Click 'Statements' in left panel
        self.find_element(By.XPATH, '//*[@accesskey="3"]').click()
        time.sleep(1 * self.multiplier)
        # Click 'Download/export transactions'
        self.find_element(By.XPATH, '//*[@id="ctl00_mainContent_SS1AALDAnchor"]').click()
        time.sleep(1 * self.multiplier)
        # Select last 4 months of transactions
        Select(self.find_element(By.XPATH, '//*[@id="ctl00_mainContent_SS6SPDDA"]')).select_by_value('M4')
        # Select CSV format
        Select(self.find_element(By.XPATH, '//*[@id="ctl00_mainContent_SS6SDDDA"]')).select_by_value('1')
        # Ensure 'Download all available accounts' checkbox is selected
        accounts_checkbox = driver.find_element(By.XPATH, '//*[@id="SelectAllChecked_SS6CBIB"]')
        if not accounts_checkbox.is_selected():
            accounts_checkbox.click()
        element = self.find_element_by_id("ctl00_mainContent_FinishButton_button")
        driver.execute_script("arguments[0].click();", element)
        time.sleep(1 * self.multiplier)
        element = self.find_element(By.XPATH, '//*[@id="ctl00_mainContent_SS7-LWLA_button_button"]')
        driver.execute_script("arguments[0].click();", element)
        time.sleep(5)

if __name__ == '__main__':
    with NatWestExport() as driver:
        driver.login()
        driver.export_transactions()
