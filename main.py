import requests
import argparse
import sys
from termcolor import cprint
from pyfiglet import figlet_format
import concurrent.futures as cf
import numpy as np
import time
import os

class ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        cprint(message.capitalize()+"\n", "red")
        cprint("Help Menu:".capitalize()+"\n", "yellow")

class BlacketUPI:
    def __init__(self, **kwargs):
        self.upi_id = kwargs.get("upi_id")
        self.upi_handles = kwargs.get("upi_handles")
        self.api_url = "https://upibankvalidator.com/api/upiValidation"
        self.threads = 15
        self.rate_limit_count = 0
        self.rate_limit_reqs_break = 15
        self.rate_limit_sleep_secs = 30

    def fetch_upi_details(self, handles_list):
        for handle in handles_list:
            while True:
                try:
                    upi_string = f"{self.upi_id}@{handle}"
                    req = requests.post(f"{self.api_url}?upi={upi_string}")
                    resp_status_code = req.status_code

                    if resp_status_code == 429:
                        self.rate_limit_count += 1
                        if self.rate_limit_count >= self.rate_limit_reqs_break:
                            cprint(f"[\U0000274C] You Have Been Rate Limited Too Many Times, Try Again Few Minutes Later", "red")
                            os.kill(os.getpid(), 9)

                        cprint(f"[\U0001F4A4] Request Limit Exceeded, Sleeping For {self.rate_limit_sleep_secs} Seconds", "yellow")
                        time.sleep(self.rate_limit_sleep_secs)
                    break

                except Exception as error:
                    cprint(f"[\U00002620] Something Went Wrong!!!, Error: {error}", "red")
                    os.kill(os.getpid(), 9)

            if resp_status_code == 400:
                cprint("[\U0000274C] Invalid UPI ID: " + upi_string, "red")
                os.kill(os.getpid(), 9)

            if resp_status_code == 200:
                resp_obj = req.json()
                is_registered = resp_obj.get("isUpiRegistered")
                name = resp_obj.get("name")
                message = resp_obj.get("message")
                if is_registered:
                    cprint("[\U00002705] UPI ID: " + upi_string + "\t\t" + f"{name}", "green")
                else:
                    cprint("[\U0000274C] UPI ID: " + upi_string + "\t\t" + f"{message}", "red")

    def lets_osint(self):
        cprint("Validating UPI ID: "+self.upi_id+"\n", "blue")
        threads = []
        nested_upi_handles = np.array_split(self.upi_handles, self.threads)

        with cf.ThreadPoolExecutor(max_workers=self.threads) as executor:
            for handles_list in nested_upi_handles:
                threads.append(executor.submit(self.fetch_upi_details, handles_list))
            
            for t in threads:
                if t.exception():
                    print("\n")
                    cprint("="*100, "red")
                    cprint(f"[\U00002620] Something Went Wrong!!!, Error: {t.exception()}", "red")
                    cprint("="*100, "red")

if __name__ == "__main__":
    cprint(figlet_format("Blacket-UPI-OSINT", font="epic"), "white", attrs=["bold"])
    cprint("[\U0001F30E] Blacklet UPI OSINT Tool can find the details about an UPI ID", "white")
    cprint("[\U0001F4DD] Created By - Xan0er\n", "white")

    usage_msg = """
        python main.py [-h] -uid <upi_id>
    """

    parser = ArgumentParser(usage=usage_msg)
    parser._action_groups.pop()

    required = parser.add_argument_group("required arguments")
    optional = parser.add_argument_group("optional arguments")
    required.add_argument("-uid", help="Enter Phone Number Or UPI ID", required=True)
    optional.add_argument("-out", help="Output Result To A File")
    args_obj = parser.parse_args()

    upi_id = args_obj.uid

    if (len(sys.argv) == 1) or (upi_id is None):
        parser.print_help()
        parser.exit()

    upi_handles = ["apl", "yapl", "abfspay", "fbl", "axisb", "idfcbank", "rmhdfcbank", "icici", "okaxis", "okhdfcbank", "paytm",
                   "okicici", "oksbi", "axisbank", "jupiteraxis", "hdfcbankjd", "indus", "hsbc", "myicici", "ikwik", "ybl", "ibl",
                   "axl", "pingpay", "kmbl", "tapicici", "timecosmos", "yesbank", "waicici", "waaxis", "wahdfcbank", "wasbi"]

    bu = BlacketUPI(upi_id=upi_id, upi_handles=upi_handles)
    bu.lets_osint()