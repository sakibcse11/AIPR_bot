import time

from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By


def check_too_many_attempts(bot):
    try:
        error_element = bot.find_elements(By.TAG_NAME, "verify-exceeded-attempts")
        if error_element:
            print("❌ Too many verification attempts. Process terminated.")
            return True
    except NoSuchElementException:
        return False
    except Exception as e:
        print(f"⚠️ Error while checking verification attempts: {e}")
        return False


def check_email_or_captcha_errors(bot):
    """Check if email or CAPTCHA input has errors after submission."""

    try:
        # Check if email field exists
        email_input = bot.find_element(By.CLASS_NAME, "iforgot-apple-id")
        email_has_error = "has-errors" in email_input.get_attribute("class")

        # Check if CAPTCHA field exists
        captcha_input = bot.find_element(By.CLASS_NAME, "captcha-input")
        captcha_has_error = "has-errors" in captcha_input.get_attribute("class")

        if email_has_error:
            print("❌ Invalid Email. Skipping to next row...")
            return "invalid_email"

        if captcha_has_error:
            print("❌ Incorrect CAPTCHA. Retrying...")
            return "retry_captcha"

        print("✅ No errors detected, proceeding to next page.")
        return "success"

    except NoSuchElementException:
        # If elements are not found, assume page changed successfully
        print("✅ No errors detected, page changed successfully.")
        return "success"

    except Exception as e:
        print(f"❌ Unexpected error while checking for input errors: {e}")
        return "error"


def check_birthday_errors(bot):
    """Check if birthday input has errors after submission."""
    time.sleep(2)
    try:
        birthday_element = bot.find_element(By.ID, "birthDate")
        if birthday_element.get_attribute("aria-invalid") == "true":
            return "invalid_date"
        elif birthday_element.get_attribute("aria-invalid") == "false":
            return "success"
        else:
            return "unexpected_error"
    except NoSuchElementException:
        return "success"
    except Exception as e:
        print(f"❌ Unexpected error while checking for input errors: {e}")
        return "unexpected_error"


def check_security_questions_errors(bot):
    """Check if security questions has errors after submission."""
    time.sleep(2)
    if check_too_many_attempts(bot):
        return "too_many_attempts"
    try:
        birthday_element = bot.find_element(By.ID, "birthDate")
        if birthday_element.get_attribute("aria-invalid") == "true":
            return "invalid_date"
        elif birthday_element.get_attribute("aria-invalid") == "false":
            return "success"
        else:
            return "unexpected_error"
    except NoSuchElementException:
        return "success"
    except Exception as e:
        print(f"❌ Unexpected error while checking for input errors: {e}")
        return "unexpected_error"
def check_errors(bot,df,index,page,next_page):
    """Check if errors has errors after submission."""
    time.sleep(2)
    current_page = bot.find_page()
    if current_page == "verify-exceeded-attempts":
        print("❌ Too many attempts, moving to next row...")
        df.at[index, 'result'] = "Too many attempts"
        return False
    if current_page == next_page:
        print("✅ Success moving to next step...")
        return True
    if current_page == page:
        if page == "birthday":
            df.at[index, 'result'] = "Invalid Birthday"
            return False
        if page == "verify-security-questions":
            df.at[index, 'result'] = "Invalid Security Questions"
            return False
        if page == "reset-password":
            df.at[index, 'result'] = "Invalid New Password"
            return False
        if page == "forgot-password":
            return False
        else:
            df.at[index, 'result'] = "Unexpected Error"
            return False
    else:
        df.at[index, 'result'] = "Unexpected Page"
        return False
