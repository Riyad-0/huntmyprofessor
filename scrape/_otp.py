import os

from dotenv import load_dotenv
import pyotp


def main():
  load_dotenv()
  otp_key = os.getenv('OTP_KEY')
  if otp_key is None:
    print('expected OTP_KEY environment variable')
    return
  
  totp = pyotp.TOTP(otp_key)
  print(totp.now())

main()