import time

from pass_reset import constants as const
from pass_reset import errors as err
import pandas as pd


def load_excel():
    """Load the Excel file and return the DataFrame."""
    return pd.read_excel(const.FILE_PATH, header=None)


def process_email_and_captcha_validation(bot, email, df, index):
    """Fill the email and captcha fields accordingly."""
    page = "forgot-password"
    next_page="recovery-options" or "authentication-method"
    if bot.enter_email(email):

        attempt = 0
        while attempt < 3:
            bot.solve_captcha()
            if err.check_errors(bot, df, index, page, next_page):
                return True
            error_status = err.check_email_or_captcha_errors(bot)

            if error_status == "invalid_email":
                df.at[index, 'result'] = "Invalid Email"
                return False

            if error_status == "retry_captcha":
                attempt += 1
                print(f"🔄 Retrying CAPTCHA... Attempt {attempt}")
                continue  # Retry CAPTCHA

            if error_status == "success":
                print("✅ Email verified, moving to next step...")
                return True  # Move to next page

        if attempt == 3:
            print("❌ Maximum CAPTCHA attempts reached. Skipping row.")
            df.at[index, 'result'] = "CAPTCHA Failed"
            return False


def process_recovery_options(bot):
    """Check if the bot options are correct."""
    page = bot.find_page()
    if page == "recovery-options":
        bot.select_recovery_options()
        time.sleep(2)
    return bot.select_authentication_method()


def process_birthday_validation(bot, date, df, index):
    """Fill the birthday fields accordingly."""
    page = "birthday"
    next_page="verify-security-questions"
    if bot.find_page() == "birthday":
        if bot.enter_birthday(date):
            return err.check_errors(bot, df, index, page, next_page)
    else:
        return False


def process_security_questions_validation(bot, df, index, sqa1, sqa2, sqa3):
    """Fill the security questions fields accordingly."""
    page = "verify-security-questions"
    next_page = "reset-password"

    if bot.find_page() == page:
        if bot.enter_security_questions(sqa1, sqa2, sqa3):
            return err.check_errors(bot, df, index, page, next_page)
    else:
        return False


def process_password_reset(bot, df, index, new_password):
    """Fill the password reset fields accordingly."""
    page = "reset-password"
    next_page = "reset-success"
    if bot.find_page() == page:
        if bot.enter_password(new_password):
            return err.check_errors(bot, df, index, page, next_page)
    else:
        return False
