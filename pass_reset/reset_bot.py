from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time
from pass_reset import constants as const
import nopecha

nopecha.api_key = const.NOPECHA_API_KEY


class PassReset(webdriver.Chrome):
    def __init__(self):
        """Initialize the PassReset class by inheriting Chrome WebDriver."""
        print("Initializing WebDriver...")
        options = webdriver.ChromeOptions()
        service = Service(ChromeDriverManager().install())
        super().__init__(service=service, options=options)

    def find_page(self):
        time.sleep(1)
        pages = {
            "forgot-password": "forgot-password",
            "recovery-options": "recovery-options",
            "authentication-method": "authentication-method",
            "birthday": "birthday",
            "verify-security-questions": "verify-security-questions",
            "reset-password": "reset-password",
            "reset-success": "reset-success",
            "verify-exceeded-attempts": "verify-exceeded-attempts",
        }
        try:
            for tag in pages:
                elements = self.find_elements(By.TAG_NAME, tag)  # Find all elements with the given tag
                if elements:  # If at least one is found
                    return tag  # Return the detected page

            return "unknown_page"  # If none of the pages are found

        except Exception as e:
            print(f"⚠️ Error in find_page: {e}")
            return "unknown_page"




    def enter_email(self, email):
        """Enter the email into the Apple ID reset form."""
        try:
            email_input = self.find_element(By.CLASS_NAME, "iforgot-apple-id")
            email_input.clear()
            email_input.send_keys(email)
            print(f"✅ Entered email: {email}")
            return True
        except Exception as e:
            print(f"❌ Error entering email {email}: {e}")
            return False

    def find_captcha_image(self):
        try:
            captcha_element = self.find_element(By.CSS_SELECTOR, "img[src^='data:image']")
            captcha_image_src = captcha_element.get_attribute("src")

            if not captcha_image_src.startswith("data:image"):
                print("❌ CAPTCHA not found.")
                return False

            # Convert image source to Base64 for NopeCHA
            captcha_image = captcha_image_src.split(",")[1]
            return captcha_image
        except Exception as e:
            print(f"❌ Error Finding Captcha Image: {e}")
            return False

    def solve_captcha(self):
        """Take a screenshot of CAPTCHA and send it to NopeCHA API."""
        try:
            captcha_image = self.find_captcha_image()
            while not captcha_image:
                new_code_image = self.find_elements(By.CLASS_NAME, "captcha-new-code")
                new_code_image[0].click()
                captcha_image = self.find_captcha_image()

            # Send CAPTCHA to NopeCHA
            response = nopecha.Recognition.solve(
                type='textcaptcha',
                image_urls=[captcha_image],
            )

            if "data" in response and response["data"]:
                solution = response["data"][0]
                print(f"✅ CAPTCHA Solved: {solution}")

                # Find CAPTCHA input box and enter the solution
                captcha_input = self.find_element(By.CLASS_NAME, "captcha-input")
                captcha_input.clear()
                captcha_input.send_keys(solution)

                # Submit CAPTCHA
                captcha_input.send_keys(Keys.RETURN)
                time.sleep(3)  # Wait for response

                return True
            else:
                print("❌ CAPTCHA solving failed.")
                return False
        except Exception as e:
            print(f"❌ Error solving CAPTCHA: {e}")
            return False

    def select_recovery_options(self):
        """Check if the recovery options page is available and click 'Continue'."""

        try:
            recovery_options = self.find_element(By.TAG_NAME, "recovery-options")
            if recovery_options:
                print("✅ Recovery options page detected.")

                # Find and click the 'Continue' button
                continue_button = self.find_element(By.ID, "action")
                continue_button.click()
                print("✅ Clicked 'Continue'")

                return True
        except NoSuchElementException:
            return False

        except Exception as e:
            print(f"❌ Recovery options not found or error clicking 'Continue': {e}")
            return False

    def select_authentication_method(self):
        """Select radio button options and click continue."""
        try:

            radio_button = self.find_element(By.ID, "optionquestions")
            self.execute_script("arguments[0].click();", radio_button)
            print("✅ Selected 'Security Questions' option.")

            # Click continue button
            continue_button = self.find_element(By.ID, "action")
            self.execute_script("arguments[0].click();", continue_button)
            print("✅ Clicked Continue button.")
            return True
        except Exception as e:
            print(f"❌ Error selecting security questions: {e}")
            return False

    def enter_birthday(self, birthday):

        try:
            # Locate the birthday input field by class (more specific) or ID
            birthday_input = self.find_element(By.CLASS_NAME, "date-input")

            # Clear any existing value in the field
            birthday_input.clear()
            time.sleep(1)

            # Enter the new birthday value
            birthday_input.send_keys(birthday)
            time.sleep(1)

            # Press ENTER (if required)
            birthday_input.send_keys(Keys.RETURN)

            print(f"✅ Birthday '{birthday}' entered successfully.")
            return True

        except Exception as e:
            print(f"❌ Error entering birthday: {e}")
            return False

    def enter_security_questions(self, sqa1, sqa2, sqa3):
        """Enter answers for the two security questions that appear."""

        # Dictionary to map IDs to answers
        sqa_answers = {
            "130": sqa1,  # Security Question 1
            "136": sqa2,  # Security Question 2
            "142": sqa3,  # Security Question 3
        }

        entered_count = 0  # Track how many questions were answered

        for sqa_id, answer in sqa_answers.items():
            if entered_count >= 2:
                break  # Stop after entering two answers

            try:
                sqa_input = self.find_element(By.ID, sqa_id)
                if sqa_input:
                    sqa_input.clear()
                    sqa_input.send_keys(answer)
                    sqa_input.send_keys(Keys.RETURN)
                    entered_count += 1
                    print(f"✅ Answered security question with ID {sqa_id}: {answer}")
            except NoSuchElementException:
                print(f"⚠️ Security question {sqa_id} not found. Skipping.")
            except Exception as e:
                print(f"❌ Error entering security answer for {sqa_id}: {e}")
                return False

        if entered_count == 2:
            print("✅ Successfully entered two security answers.")
            return True
        else:
            print("❌ Could not find two security questions. Something is wrong.")
            return False

    def enter_password(self, new_password):
        try:
            # Find the second password field dynamically
            password_fields = self.find_elements(By.CSS_SELECTOR, "input[type='password']")
            for field in password_fields:
                field.clear()
                field.send_keys(new_password)
                print("✅ Entered password")
                field.send_keys(Keys.RETURN)

            return True
        except NoSuchElementException:
            print("❌ Second password field not found!")
        except Exception as e:
            print(f"❌ Error entering password in second field: {e}")
            return False

    def __exit__(self, exc_type, exc_value, traceback):
        """Ensure the WebDriver quits on exit."""
        self.quit()
