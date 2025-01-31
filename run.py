import time

import pass_reset.constants as const
from pass_reset.reset_bot import PassReset
import pass_reset.process as process


def main():
    df = process.load_excel()
    df.columns = ['email', 'current_pass', 'sqa1', 'sqa2', 'sqa3',
                  'birth_day', 'new_pass']

    with PassReset() as bot:
        for index, row in df.iterrows():
            bot.get(const.APPLE_RESET_URL)  # Reload URL
            time.sleep(2)
            email = row['email']
            birthday = row['birth_day'].strftime('%m/%d/%Y')
            sqa1 = row['sqa1']
            sqa2 = row['sqa2']
            sqa3 = row['sqa3']
            new_pass = row['new_pass']

            process1 = process.process_email_and_captcha_validation(bot,email,df,index)
            if process1:
                print("moving to process 2")
                process2 = process.process_recovery_options(bot)
                if process2:
                    process3 = process.process_birthday_validation(bot,birthday,df,index)
                    if process3:
                        print("initializing process 4")
                        process4 = process.process_security_questions_validation(bot,df,index,sqa1,sqa2,sqa3)
                        if process4:
                            process5 = process.process_password_reset(bot,df,index,new_pass)
                            if process5:
                                df.at[index, 'current_pass'] = new_pass
                                df.at[index, 'result'] = "success"
                    else:
                        continue
                else:
                    continue
            else:
                continue
    df.to_excel(const.OUTPUT_FILE_PATH, index=False)  # Save results

if __name__ == "__main__":
    main()
