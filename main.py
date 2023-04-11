import openai
import requests
import signal
from pyfiglet import figlet_format
import argparse
from bs4 import BeautifulSoup
import sys
from termcolor import cprint
from alive_progress import alive_bar

import os
import http.client
import io
import threading

sys.path.append("sc")

from sc.colors import Bcolors
from sc.neurocrawler import web_crawler
from sc.api_enum import api_enumeration
from sc.version import ver_ger
from sc.subdomains import subdomain

def signal_handler(sig, frame):
    print("\nThe programm is terminated by the user.")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


def print_banner():
    print()
    cprint(figlet_format('GPTBUSTER', font='starwars', width=200),
           'yellow', attrs=['bold'])


print_banner()

print(Bcolors.HEADER + 'GPT-based web-dir fuzzer, crawler')
print(Bcolors.HEADER + '@wearetyomsmnv')
print(Bcolors.OKGREEN + 'web fuzzing,crawling,enumerator for penetration testers with <3')

print(Bcolors.BOLD)
commands = argparse.ArgumentParser(description='Basic parameters')
commands.add_argument('link', help='Provide a link to a web resource')
commands.add_argument('api_key', help='Specify the api-key for chat-gpt')
commands.add_argument('temperature', type=float, help='Specify the temperature for parameters [0.00 to 1.00]')
commands.add_argument('--insecure', action='store_true', help='Search for unsafe directories')
commands.add_argument('--backup', action='store_true', help='Searching for backups')
commands.add_argument('--subdomains', action='store_true', help='Listing of subdomains')
commands.add_argument('--api_enum', action='store_true', help='Fuzzing by api')
commands.add_argument('--crawler', action='store_true', help='Black-box crawler')
commands.add_argument('--output', action='store_true', default=False, help='.txt output')
commands.add_argument('--cookies', nargs='?', type=str,  default=False, help='Add self cookies for request')
commands.add_argument('--response', action='store_true', default=False, help='View responses for all requests')
commands.add_argument('--headers', action='store_true', default=False, help='View headers for all requests')
commands.add_argument('--head', action='store_true', default=False, help='Add custom headers in request head')
commands.add_argument('--r', nargs='?', type=str,  default=False, help='Add your request file')
commands.add_argument('--x', nargs='?', type=str,  default=False, help='Change default http method (get, post, put, delete)')
commands.add_argument('--proxy', action='store_true', default=False, help='Use proxy for requests')


args1 = commands.parse_args()

link = args1.link
api_key = args1.api_key
insecure = args1.insecure
backups = args1.backup
subdomains = args1.subdomains
api_enum = args1.api_enum
crawler = args1.crawler
output = args1.output
temp = args1.temperature
cookies = args1.cookies
responses = args1.response
headeers = args1.headers
head = args1.head
requ = args1.r
method_req = args1.x
proxy = args1.proxy

if not any([link, api_key, temp]):
    print(Bcolors.FAIL + "[FAIL:] " + 'You have not specified the main arguments')
    print(Bcolors.FAIL + "[NOTE:] " + 'Try again')
    sys.exit(0)

if not any([insecure, backups, subdomains,
            api_enumeration, crawler, output, cookies, responses, headeers, head, requ, method_req, proxy]):
    print(Bcolors.FAIL + "[FAIL:] " + 'You have not specified additional arguments')
    print(Bcolors.FAIL + "[NOTE:] " + 'Try again')
    sys.exit(0)

openai.api_key = api_key


version = ver_ger(openai.api_key)

print(Bcolors.HEADER + version)


if proxy:
    print("Proxy")
    protocol = input(str("Specify a protocol[http, https]:"))
    if protocol not in ("http", "https"):
        print("Incorrect protocol for the proxy is specified")
        sys.exit(0)
    prox = input(str("Specify a proxy (ex: 'http://proxy_host:proxy_port')"))
    proxies = {protocol: prox}
else:
    proxies = None

if temp > 1.00:
    print(Bcolors.FAIL + "[-]: " + "Specify a lower temperature. Openai API does not accept values greater than 1.00")
    sys.exit(0)
else:
    print(Bcolors.OKGREEN + f"Tempereature is: {temp}.")

directories_dict = {}
directories_dict2 = {}
detected_cms = ""
detected_api = ""
txtman = ""


cookies = {'Cookie': args1.cookies} if args1.cookies else {}

headers = None

if args1.x:
    if args1.x.lower() == "get":
        method = "get"
    elif args1.x.lower() == "post":
        method = "post"
    elif args1.x.lower() == "put":
        method = "put"
    elif args1.x.lower() == "delete":
        method = "delete"
    else:
        print("You have specified a non-existent http method (--x GET,POST,PUT or DELETE)")
        sys.exit(0)
else:
    method = "get"


if requ:
    if head:
        print("You cannot use the request file with other headers. Remove --head flag.")
        sys.exit(0)
    else:
        with open(args1.r, 'r') as f:
            request_text = f.read()

        request_bytes = bytes(request_text, encoding='utf-8')
        request_io = io.BytesIO(request_bytes)

        request_headers = http.client.parse_headers(request_io, _class=http.client.HTTPMessage)

        headers = dict(request_headers.items())


if head:
    print("Add custom http headers in request.")
    while True:
        header = input("Enter header in format {name}:{value} or type 'done' to stop: ")
        if header.lower() == 'done':
            break
        elif ':' in header:
            name, value = header.split(':', maxsplit=1)
            headers[name.strip()] = value.strip()
        else:
            print("Invalid header format. Please try again.")
            headers = {}

    
def check_files(dictionary_dir, link, headers, cookies):
    directories = []
    print(Bcolors.OKCYAN + "[+]: " + "TESTING IS GOING ON")
    with alive_bar(len(dictionary_dir)) as bar:
        for key, directory in dictionary_dir.items():
            url = f"{link.lstrip('/')}{directory}"
            response = requests.request(method, url, headers=headers, cookies=cookies, timeout=5, proxies=proxies)
            if response.status_code == 200:
                directories.append(f"{Bcolors.OKGREEN}[+]{Bcolors.ENDC} {key}: {url}")
                if args1.response:
                    print(Bcolors.OKCYAN + "[+]" + "[response]" + "Http-code:\n")
                    print(response.text)
                    print(Bcolors.OKCYAN + "[+]" + "[response]" + f"Cookies:\n")
                    print(response.cookies)
                if args1.headers:
                    print(Bcolors.OKCYAN + "[+]" + "[headers]: ")
                    print(response.headers)
            else:
                directories.append(f"{Bcolors.FAIL}[-]{Bcolors.ENDC} {key}: {url}")
            bar()
    return directories


def gpt(cms):
    print(
        Bcolors.OKCYAN + '[+]: ' + "Enter your parameter to generate the dictionary via chatgpt or write 'default':")
    parametr = input(str("param: "))
    if parametr == "default":
        paramet = f"Please generate a large list of {cms} directories and files that you know.\n"
    else:
        paramet = parametr

    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=(

            f"{paramet}.Just display the list of directories without your explanations.\n"
        ),
        temperature=temp,
        max_tokens=2048,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=["\n\n"],
    )

    status = response.choices[0].text.split('\n')

    result_dict = {i: '/'.join([s.strip() for s in item.split('/')]).replace('//', '/') for i, item in enumerate(status)
                   if item.strip()}

    print(Bcolors.OKCYAN + "[+]: " + "THE DICTIONARY IS READY")

    return result_dict


results = check_files(directories_dict, link, headers, cookies)
for result in results:
    print(result)


def check_wordpress(linked):
    response = requests.request(method, f"{linked}wp-login.php", headers=headers, cookies=cookies, timeout=5, proxies=proxies)
    if response.status_code == 200:
        if args1.response:
            print(Bcolors.OKCYAN + "[+]" + "[response]" + "Http-code:\n")
            print(response.text)
            print(Bcolors.OKCYAN + "[+]" + "[response]" + f"Cookies:\n")
            print(response.cookies)
        if args1.headers:
            print(Bcolors.OKCYAN + "[+]" + "[headers]: ")
            print(response.headers)
        return True

    response = requests.request(method, f"{linked}wp-includes/", headers=headers, cookies=cookies, timeout=5, proxies=proxies)
    if response.status_code == 200:
        if args1.response:
            print(Bcolors.OKCYAN + "[+]" + "[response]" + "Http-code:\n")
            print(response.text)
            print(Bcolors.OKCYAN + "[+]" + "[response]" + f"Cookies:\n")
            print(response.cookies)
        if args1.headers:
            print(Bcolors.OKCYAN + "[+]" + "[headers]: ")
            print(response.headers)
        soup = BeautifulSoup(response.text, "html.parser")
        if soup.find("meta", {"name": "generator", "content": "WordPress"}):
            return True

    return False


def check_woocommerce(link):
    response = requests.request(method, link, headers=headers, cookies=cookies, timeout=5, proxies=proxies)
    if response.status_code == 200:
        if args1.response:
            print(Bcolors.OKCYAN + "[+]" + "[response]" + "Http-code:\n")
            print(response.text)
            print(Bcolors.OKCYAN + "[+]" + "[response]" + f"Cookies:\n")
            print(response.cookies)
        if args1.headers:
            print(Bcolors.OKCYAN + "[+]" + "[headers]: ")
            print(response.headers)
        soup = BeautifulSoup(response.text, "html.parser")
        if soup.find("meta", {"name": "generator", "content": "WooCommerce"}):
            return True

    return False


def check_joomla(linked):
    response = requests.request(method, f"{linked}administrator/", headers=headers, cookies=cookies, timeout=5, proxies=proxies)
    if response.status_code == 200:
        if args1.response:
            print(Bcolors.OKCYAN + "[+]" + "[response]" + "Http-code:\n")
            print(response.text)
            print(Bcolors.OKCYAN + "[+]" + "[response]" + f"Cookies:\n")
            print(response.cookies)
        if args1.headers:
            print(Bcolors.OKCYAN + "[+]" + "[headers]: ")
            print(response.headers)
        soup = BeautifulSoup(response.text, "html.parser")
        if soup.find("meta", {"name": "generator", "content": "Joomla!"}):
            return True

    response = requests.request(method, f"{linked}templates/", headers=headers, cookies=cookies, timeout=5, proxies=proxies)
    if response.status_code == 200:
        if args1.response:
            print(Bcolors.OKCYAN + "[+]" + "[response]" + "Http-code:\n")
            print(response.text)
            print(Bcolors.OKCYAN + "[+]" + "[response]" + f"Cookies:\n")
            print(response.cookies)
        if args1.headers:
            print(Bcolors.OKCYAN + "[+]" + "[headers]: ")
            print(response.headers)
        soup = BeautifulSoup(response.text, "html.parser")
        if soup.find("meta", {"name": "generator", "content": "Joomla!"}):
            return True

    response = requests.request(method, f"{linked}components/", headers=headers, cookies=cookies, timeout=5)
    if response.status_code == 200:
        if args1.response:
            print(Bcolors.OKCYAN + "[+]" + "[response]" + "Http-code:\n")
            print(response.text)
            print(Bcolors.OKCYAN + "[+]" + "[response]" + f"Cookies:\n")
            print(response.cookies)
        if args1.headers:
            print(Bcolors.OKCYAN + "[+]" + "[headers]: ")
            print(response.headers)
        soup = BeautifulSoup(response.text, "html.parser")
        if soup.find("meta", {"name": "generator", "content": "Joomla!"}):
            return True

    return False


def check_drupal(linked):
    response = requests.request(method, f"{linked}modules/", headers=headers, cookies=cookies, timeout=5)
    if response.status_code == 200:
        if args1.response:
            print(Bcolors.OKCYAN + "[+]" + "[response]" + "Http-code:\n")
            print(response.text)
            print(Bcolors.OKCYAN + "[+]" + "[response]" + f"Cookies:\n")
            print(response.cookies)
        if args1.headers:
            print(Bcolors.OKCYAN + "[+]" + "[headers]: ")
            print(response.headers)
        soup = BeautifulSoup(response.text, "html.parser")
        if soup.find("meta", {"name": "generator", "content": "Drupal"}):
            return True

    return False


def check_shopify(link):
    response = requests.request(method, link, headers=headers, cookies=cookies, timeout=5)
    if response.status_code == 200:
        if args1.response:
            print(Bcolors.OKCYAN + "[+]" + "[response]" + "Http-code:\n")
            print(response.text)
            print(Bcolors.OKCYAN + "[+]" + "[response]" + f"Cookies:\n")
            print(response.cookies)
        if args1.headers:
            print(Bcolors.OKCYAN + "[+]" + "[headers]: ")
            print(response.headers)
        soup = BeautifulSoup(response.text, "html.parser")
        if soup.find("meta", {"name": "generator", "content": "Shopify"}):
            return True

    return False


def check_1c_bitrix(linked):
    response = requests.request(method, f"{linked}bitrix/", headers=headers, cookies=cookies, timeout=5)
    if response.status_code == 200:
        if args1.response:
            print(Bcolors.OKCYAN + "[+]" + "[response]" + "Http-code:\n")
            print(response.text)
            print(Bcolors.OKCYAN + "[+]" + "[response]" + f"Cookies:\n")
            print(response.cookies)
        if args1.headers:
            print(Bcolors.OKCYAN + "[+]" + "[headers]: ")
            print(response.headers)
        soup = BeautifulSoup(response.text, "html.parser")
        if soup.find("meta", {"name": "generator", "content": "1C-Bitrix"}):
            return True

    return False


def detect_cms(link, headers, cookies):
    response = requests.request(method, link, headers=headers, cookies=cookies, timeout=5)
    soup = BeautifulSoup(response.text, "html.parser")

    if soup.find("meta", {"name": "generator", "content": "WordPress"}) or \
            soup.find_all("link", rel="stylesheet", href=lambda href: href and "wp-content" in href) or \
            soup.find("script", {"id": "wp-emoji-release"}):
        return "WordPress"

    if soup.find("meta", {"name": "generator", "content": "WooCommerce"}) or \
            soup.find_all("link", rel="stylesheet", href=lambda href: href and "woocommerce" in href) or \
            soup.find("script", {"src": lambda src: src and "woocommerce" in src}):
        return "WooCommerce"

    if soup.find("meta", {"name": "generator", "content": "Shopify"}) or \
            soup.find_all("link", rel="stylesheet", href=lambda href: href and "shopify" in href) or \
            soup.find("script", {"src": lambda src: src and "shopify" in src}):
        return "Shopify"

    elif soup.find("meta", {"name": "generator", "content": "Joomla!"}) or \
            soup.find_all("link", rel="stylesheet", href=lambda href: href and "joomla" in href) or \
            soup.title and "Joomla!" in soup.title.string:
        return "Joomla"

    elif soup.find("meta", {"name": "generator", "content": "Drupal"}):
        return "Drupal"

    elif soup.find("meta", {"name": "generator", "content": "1C-Bitrix"}) or \
            soup.find_all("link", rel="stylesheet", href=lambda href: href and "bitrix" in href):
        return "1C-Bitrix"

    else:
        return Bcolors.FAIL + "Not defined"


detected_cms = detect_cms(link, headers, cookies)
print(Bcolors.OKGREEN + f"Detected CMS: {detected_cms}")


def insecure(detected_cms):
    print(Bcolors.OKGREEN + "[+]: " + "CHECK INSECURE DIR")

    reg = True

    def gpt_insecure(cms, paramet=""):

        if paramet == "":
            print(
                Bcolors.OKCYAN + '[+]: ' + f"Enter your parameter to generate the {detected_cms} dictionary via chatgpt or write 'default': ")
        else:
            print(Bcolors.OKCYAN + f'[+]: The specified parameter is used: {paramet}')

        print(
            Bcolors.OKCYAN + '[TYPE]: ' + "Use ' - as a quotation mark. Do not write jailbreak here")

        if paramet == "default":
            paramet = f"Please generate a big list of insecure directories and parameters for {detected_cms} that you know.Just display the list of directories without your explanations.\n"
        elif paramet == "":
            paramet = input(str("param: "))

        desc = "This list will be used to look for unsafe directories and parameters"

        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=(
                f"{desc}{paramet}.Just display the list of directories without your explanations.\n"
            ),
            temperature=temp,
            max_tokens=2048,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop=["\n\n"],
        )

        status = response.choices[0].text.split('\n')

        result_dict = {i: '/'.join([s.strip() for s in item.split('/')]).replace('//', '/') for i, item in
                       enumerate(status) if item.strip()}

        print(Bcolors.OKCYAN + "[+]: " + "THE DICTIONARY IS READY")

        return result_dict

    last_insecure_files = None
    last_paramet = None

    while reg:
        detected_cms = "CMS: " + detect_cms(link, headers, cookies)
        print(Bcolors.OKGREEN + f"Detected CMS: {detected_cms}")

        if last_insecure_files is None:
            paramet = input(str("[+] Enter your parameter to generate a list of unsafe files or write 'default':"))
            insecure_files = gpt_insecure(detected_cms, paramet)
        else:
            print(Bcolors.OKCYAN + '[+]: ' + "Do you want to continue with the previous request? [yes/new]")
            choice = input(str("Answer: "))
            if choice.lower() == "yes":
                insecure_files = last_insecure_files
                paramet = input(
                    str("[+] Enter your parameter to generate a list of unsafe files (leave blank to use the previous prompt):"))
                if paramet == "":
                    paramet = last_paramet
            else:
                paramet = input(str("[+] Enter your parameter to generate a list of unsafe files:"))
                insecure_files = gpt_insecure(detected_cms, paramet)

        last_insecure_files = insecure_files
        last_paramet = paramet

        results = check_files(directories_dict, link, headers, cookies)
        for result in results:
            print(result)

        results_insecure = check_files(insecure_files, link, headers, cookies)
        if txtman:
            name = input(str("Enter a name for the file:"))
            with open(f"{name}.txt", "w") as f:
                for result in results_insecure:
                    f.write(result)
                f.close()
                print(f"File name {name}.txt was created in {os.getcwd()} ")
        else:
            for result in results_insecure:
                print(result)

        print(Bcolors.OKCYAN + "[?]: " + "TRY AGAIN? [Yes/no]")
        usl = input(str("Answer: "))
        if usl.lower() == "yes":
            continue
        else:
            break


def backups(detected_cms):
    reg = True

    print(Bcolors.OKGREEN + "[+]: " + "CHECK BACKUP FILES")

    def gpt_backups(cms, paramet=""):
        if paramet == "":
            print(
                Bcolors.OKCYAN + '[+]: ' + "Enter your parameter to generate a list of backup files via chatgpt or write 'default': ")
        else:
            print(Bcolors.OKCYAN + f'[+]: The specified parameter is used: {paramet}')

        print(
            Bcolors.OKCYAN + '[TYPE]: ' + "Use ' - as a quotation mark. Do not write jailbreak here")
        if paramet == "default":
            paramet = f"Please generate a big list of files that can be backups for {detected_cms} that you know.\n"
        elif paramet == "":
            paramet = input(str("param: "))
        desc = "This list will be used to search for backups on the website."

        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=(
                f"{desc}{paramet}.Just display a list of backup files and directories without your explanations.\n"
            ),
            temperature=temp,
            max_tokens=2048,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop=["\n\n"],
        )

        status = response.choices[0].text.split('\n')

        result_dict = {i: '/'.join([s.strip() for s in item.split('/')]).replace('//', '/') for i, item in
                       enumerate(status) if item.strip()}

        print(Bcolors.OKCYAN + "[+]: " + "THE DICTIONARY IS READY")

        return result_dict

    last_backups = None
    last_paramet = None

    while reg:
        if last_backups is None:
            paramet = input(str("[+] Enter your parameter to generate a list of backup files:"))
            backups_files = gpt_backups(detected_cms, paramet)
        else:
            print(Bcolors.OKCYAN + '[+]: ' + "Do you want to continue with the previous request? [yes/new]")
            choice = input(str("Answer: "))
            if choice.lower() == "yes":
                backups_files = last_backups
                paramet = input(
                    str("[+] Enter your parameter to generate a list of backup files (leave blank to use the previous query): "))
                if paramet == "":
                    paramet = last_paramet
            else:
                paramet = input(str("[+] Enter your parameter to generate a list of backup files: "))
                backups_files = gpt_backups(detected_cms, paramet)

        last_backups = backups_files
        last_paramet = paramet

        results_backups = check_files(backups_files, link, headers, cookies)

        if txtman:
            name = input(str("Enter a name for the file: "))
            with open(f"{name}.txt", "w") as f:
                for result in results_backups:
                    f.write(result)
                f.close()
                print(f"File name {name}.txt was created in {os.getcwd()} ")
        else:
            for result in results_backups:
                print(result)

        print(Bcolors.OKCYAN + "[?]: " + "TRY NOW ?[Yes/no]")
        usl = input(str("Answer: "))
        if usl.lower() == "yes":
            continue
        else:
            break


if __name__ == '__main__':
    if args1.output:
        txtman = True
    if args1.backup:
        backups(detected_cms)
    if args1.subdomains:
        t1 = threading.Thread(target=subdomain, args=(link, api_key, temp, headers, cookies, args1.response, method, proxies, txtman))
        t1.start()
    if args1.insecure:
        t2 = threading.Thread(target=insecure, args=(detected_cms, headers, cookies, args1.response, args1.headers, method, proxies))
        t2.start()
    if args1.api_enum:
        t3 = threading.Thread(target=api_enumeration, args=(link, api_key, temp, headers, cookies, args1.response, args1.headers, method, proxies))
        t3.start()
    if args1.crawler:
        t4 = threading.Thread(target=web_crawler, args=(link, api_key, temp, headers, cookies, args1.response, args1.headers, method, proxies))
        t4.start()
