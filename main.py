import openai
import requests
import signal
from pyfiglet import figlet_format
import argparse
from bs4 import BeautifulSoup
import sys
from termcolor import cprint
from alive_progress import alive_bar
from urllib.parse import urlsplit, urlunsplit
import os
import base64

sys.path.append("sc")

from sc.colors import Bcolors
from sc.neurocrawler import web_crawler
from sc.api_enum import api_enumeration


def signal_handler(sig, frame):
    print("\nПрограмма завершена пользователем.")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


def print_banner():
    print()
    cprint(figlet_format('GPTBUSTER', font='starwars', width=200),
           'yellow', attrs=['bold'])


print_banner()

print(Bcolors.HEADER + 'build 1.3.5')
print(Bcolors.HEADER + 'GPT-based web-dir fuzzer, crawler')
print(Bcolors.HEADER + '@wearetyomsmnv')
print(Bcolors.OKGREEN + 'web fuzzing,crawling,enumerator for penetration testers with <3')

print(Bcolors.BOLD)
commands = argparse.ArgumentParser(description='Основные параметры')
commands.add_argument('link', help='Укажите ссылку на веб-ресурс')
commands.add_argument('api_key', help='Укажите api-key для chat-gpt')
commands.add_argument('temperature', type=float, help='Укажите температуру для параметров [от 0.00 до 1.00]')
commands.add_argument('--insecure', action='store_true', help='Поиск небезопасных директорий')
commands.add_argument('--backup', action='store_true', help='Поиск бекапов')
commands.add_argument('--subdomains', action='store_true', help='Перечисление субдоменов')
commands.add_argument('--api_enum', action='store_true', help='Фаззинг по апи')
commands.add_argument('--crawler', action='store_true', help='Black-box crawler')
commands.add_argument('--output', action='store_true', default=False, help='.txt output')
commands.add_argument('--cookies', nargs='?', type=str,  default=False, help='Add self cookies for request')
commands.add_argument('--basic_auth', nargs='?', type=str,  default=False, help='Add auth data in Authentification(log:pass)')
commands.add_argument('--b64', action='store_true', default=False, help='base64 for data in Authentification')
commands.add_argument('--response', action='store_true', default=False, help='View responses for all requests')


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
basic_auth = args1.basic_auth
b64 = args1.b64
responses = args1.response

if not any([link, api_key, temp]):
    print(Bcolors.FAIL + "[FAIL:] " + 'Вы не указали основные аргументы')
    print(Bcolors.FAIL + "[NOTE:] " + 'Попробуйте ещё раз')
    sys.exit()

if not any([insecure, backups, subdomains,
            api_enumeration, crawler, output, cookies, basic_auth, b64, responses]):
    print(Bcolors.FAIL + "[FAIL:] " + 'Вы не указали дополнительные аргументы')
    print(Bcolors.FAIL + "[NOTE:] " + 'Попробуйте ещё раз')
    sys.exit()

openai.api_key = api_key

if temp > 1.00:
    print(Bcolors.FAIL + "[-]: " + "Укажите температуру меньше. openai API не принимает значения больше чем 1.00")
    sys.exit()
else:
    print(Bcolors.OKGREEN + f"Температура: {temp}.")

directories_dict = {}
directories_dict2 = {}
detected_cms = ""
detected_api = ""
txtman = ""

if b64:
    if args1.basic_auth:
        args1.basic_auth = base64.b64encode(args1.basic_auth)
    else:
        print("Вы не выбрали аргумент --basic_auth")
        sys.exit()


cookies = {'Cookie': args1.cookies,
            'User-agent': 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
           } if args1.cookies else {}
headers = {'Authorization': args1.basic_auth,
           'User-agent': 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'} if args1.basic_auth else {}


def check_files(dictionary_dir, link, headers, cookies):
    directories = []
    print(Bcolors.OKCYAN + "[+]: " + "ИДЁТ ПРОВЕРКА")
    with alive_bar(len(dictionary_dir)) as bar:
        for key, directory in dictionary_dir.items():
            url = f"{link.lstrip('/')}{directory}"
            response = requests.get(url, headers=headers, cookies=cookies)
            if response.status_code == 200:
                directories.append(f"{Bcolors.OKGREEN}[+]{Bcolors.ENDC} {key}: {url}")
                if args1.response:
                    print(Bcolors.OKCYAN + "[+]" + "[response]" + "Http-code:\n")
                    print(response.text)
                    print(Bcolors.OKCYAN + "[+]" + "[response]" + f"Cookies:\n")
                    print(response.cookies)
            else:
                directories.append(f"{Bcolors.FAIL}[-]{Bcolors.ENDC} {key}: {url}")
            bar()
    return directories


def gpt(cms):
    print(
        Bcolors.OKCYAN + '[+]: ' + "Введите свой параметр для генерации словаря через chatgpt или напишите 'default': ")
    parametr = input(str("param: "))
    if parametr == "default":
        paramet = f"Сгенерируй пожалуйста большой список директорий и файлов {cms}, которые ты знаешь.\n"
    else:
        paramet = parametr

    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=(
            f"{paramet}.Просто выведи список директорий без своих пояснений.\n"
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

    print(Bcolors.OKCYAN + "[+]: " + "СЛОВАРЬ ГОТОВ")

    return result_dict


results = check_files(directories_dict, link, headers, cookies)
for result in results:
    print(result)


def check_wordpress(linked):
    response = requests.get(f"{linked}wp-login.php", headers=headers, cookies=cookies)
    if response.status_code == 200:
        if args1.response:
            print(Bcolors.OKCYAN + "[+]" + "[response]" + "Http-code:\n")
            print(response.text)
            print(Bcolors.OKCYAN + "[+]" + "[response]" + f"Cookies:\n")
            print(response.cookies)
        return True

    response = requests.get(f"{linked}wp-includes/", headers=headers, cookies=cookies)
    if response.status_code == 200:
        if args1.response:
            print(Bcolors.OKCYAN + "[+]" + "[response]" + "Http-code:\n")
            print(response.text)
            print(Bcolors.OKCYAN + "[+]" + "[response]" + f"Cookies:\n")
            print(response.cookies)
        soup = BeautifulSoup(response.text, "html.parser")
        if soup.find("meta", {"name": "generator", "content": "WordPress"}):
            return True

    return False


def check_woocommerce(link):
    response = requests.get(link, headers=headers, cookies=cookies)
    if response.status_code == 200:
        if args1.response:
            print(Bcolors.OKCYAN + "[+]" + "[response]" + "Http-code:\n")
            print(response.text)
            print(Bcolors.OKCYAN + "[+]" + "[response]" + f"Cookies:\n")
            print(response.cookies)
        soup = BeautifulSoup(response.text, "html.parser")
        if soup.find("meta", {"name": "generator", "content": "WooCommerce"}):
            return True

    return False


def check_joomla(linked):
    response = requests.get(f"{linked}administrator/", headers=headers, cookies=cookies)
    if response.status_code == 200:
        if args1.response:
            print(Bcolors.OKCYAN + "[+]" + "[response]" + "Http-code:\n")
            print(response.text)
            print(Bcolors.OKCYAN + "[+]" + "[response]" + f"Cookies:\n")
            print(response.cookies)
        soup = BeautifulSoup(response.text, "html.parser")
        if soup.find("meta", {"name": "generator", "content": "Joomla!"}):
            return True

    response = requests.get(f"{linked}templates/", headers=headers, cookies=cookies)
    if response.status_code == 200:
        if args1.response:
            print(Bcolors.OKCYAN + "[+]" + "[response]" + "Http-code:\n")
            print(response.text)
            print(Bcolors.OKCYAN + "[+]" + "[response]" + f"Cookies:\n")
            print(response.cookies)
        soup = BeautifulSoup(response.text, "html.parser")
        if soup.find("meta", {"name": "generator", "content": "Joomla!"}):
            return True

    response = requests.get(f"{linked}components/", headers=headers, cookies=cookies)
    if response.status_code == 200:
        if args1.response:
            print(Bcolors.OKCYAN + "[+]" + "[response]" + "Http-code:\n")
            print(response.text)
            print(Bcolors.OKCYAN + "[+]" + "[response]" + f"Cookies:\n")
            print(response.cookies)
        soup = BeautifulSoup(response.text, "html.parser")
        if soup.find("meta", {"name": "generator", "content": "Joomla!"}):
            return True

    return False


def check_drupal(linked):
    response = requests.get(f"{linked}modules/", headers=headers, cookies=cookies)
    if response.status_code == 200:
        if args1.response:
            print(Bcolors.OKCYAN + "[+]" + "[response]" + "Http-code:\n")
            print(response.text)
            print(Bcolors.OKCYAN + "[+]" + "[response]" + f"Cookies:\n")
            print(response.cookies)
        soup = BeautifulSoup(response.text, "html.parser")
        if soup.find("meta", {"name": "generator", "content": "Drupal"}):
            return True

    return False


def check_shopify(link):
    response = requests.get(link, headers=headers, cookies=cookies)
    if response.status_code == 200:
        if args1.response:
            print(Bcolors.OKCYAN + "[+]" + "[response]" + "Http-code:\n")
            print(response.text)
            print(Bcolors.OKCYAN + "[+]" + "[response]" + f"Cookies:\n")
            print(response.cookies)
        soup = BeautifulSoup(response.text, "html.parser")
        if soup.find("meta", {"name": "generator", "content": "Shopify"}):
            return True

    return False


def check_1c_bitrix(linked):
    response = requests.get(f"{linked}bitrix/", headers=headers, cookies=cookies)
    if response.status_code == 200:
        if args1.response:
            print(Bcolors.OKCYAN + "[+]" + "[response]" + "Http-code:\n")
            print(response.text)
            print(Bcolors.OKCYAN + "[+]" + "[response]" + f"Cookies:\n")
            print(response.cookies)
        soup = BeautifulSoup(response.text, "html.parser")
        if soup.find("meta", {"name": "generator", "content": "1C-Bitrix"}):
            return True

    return False


def detect_cms(link, headers, cookies):
    response = requests.get(link, headers=headers, cookies=cookies)
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
        return Bcolors.FAIL + "Не определено"


detected_cms = detect_cms(link, headers, cookies)
print(Bcolors.OKGREEN + f"Detected CMS: {detected_cms}")


def insecure(detected_cms):
    print(Bcolors.OKGREEN + "[+]: " + "CHECK INSECURE DIR")

    reg = True

    def gpt_insecure(cms, paramet=""):

        if paramet == "":
            print(
                Bcolors.OKCYAN + '[+]: ' + f"Введите свой параметр для генерации словаря {cms} через chatgpt или напишите 'default': ")
        else:
            print(Bcolors.OKCYAN + f'[+]: Используется заданный параметр: {paramet}')

        print(
            Bcolors.OKCYAN + '[TYPE]: ' + "Используйте ' - как знак ковычки. Не пишите сюда jailbreak")

        if paramet == "default":
            paramet = f"Сгенерируй пожалуйста большой список небезопасных директорий и параметров для {cms}, которые ты знаешь.Просто выведи список директорий без своих пояснений.\n"
        elif paramet == "":
            paramet = input(str("param: "))

        desc = "Этот список будет использоваться для поиска небезопасных директорий и параметров"

        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=(
                f"{desc}{paramet}.Просто выведи список директорий без своих пояснений.\n"
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

        print(Bcolors.OKCYAN + "[+]: " + "СЛОВАРЬ ГОТОВ")

        return result_dict

    last_insecure_files = None
    last_paramet = None

    while reg:
        detected_cms = "CMS: " + detect_cms(link, headers, cookies)
        print(Bcolors.OKGREEN + f"Detected CMS: {detected_cms}")

        if last_insecure_files is None:
            paramet = input(str("[+] Введите свой параметр для генерации списка небезопасных файлов: "))
            insecure_files = gpt_insecure(detected_cms, paramet)
        else:
            print(Bcolors.OKCYAN + '[+]: ' + "Хотите продолжить с предыдущим запросом? [yes/new]")
            choice = input(str("Ответ: "))
            if choice.lower() == "yes":
                insecure_files = last_insecure_files
                paramet = input(
                    str("[+] Введите свой параметр для генерации списка небезопасных файлов (оставьте пустым для использования предыдущего запроса): "))
                if paramet == "":
                    paramet = last_paramet
            else:
                paramet = input(str("[+] Введите свой параметр для генерации списка небезопасных файлов: "))
                insecure_files = gpt_insecure(detected_cms, paramet)

        last_insecure_files = insecure_files
        last_paramet = paramet

        results = check_files(directories_dict, link, headers, cookies)
        for result in results:
            print(result)

        results_insecure = check_files(insecure_files, link, headers, cookies)
        if txtman:
            name = input(str("Введите имя для файла: "))
            with open(f"{name}.txt", "w") as f:
                for result in results_insecure:
                    f.write(result)
                f.close()
                print(f"File name {name}.txt was created in {os.getcwd()} ")
        else:
            for result in results_insecure:
                print(result)

        print(Bcolors.OKCYAN + "[?]: " + "ПОПРОБОВАТЬ СНОВА ?[Yes/no]")
        usl = input(str("Ответ: "))
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
                Bcolors.OKCYAN + '[+]: ' + "Введите свой параметр для генерации списка файлов бэкапов через chatgpt или напишите 'default': ")
        else:
            print(Bcolors.OKCYAN + f'[+]: Используется заданный параметр: {paramet}')

        print(
            Bcolors.OKCYAN + '[TYPE]: ' + "Используйте ' - как знак ковычки. Не пишите сюда jailbreak")
        if paramet == "default":
            paramet = f"Сгенерируй пожалуйста большой список файлов, которые могут являться бэкапами для {cms}, которые ты знаешь.\n"
        elif paramet == "":
            paramet = input(str("param: "))
        desc = "Этот список будет использоваться для поиска бэкапов на сайте."

        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=(
                f"{desc}{paramet}.Просто выведи список бэкап файлов и директорий без своих пояснений.\n"
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

        print(Bcolors.OKCYAN + "[+]: " + "СЛОВАРЬ ГОТОВ")

        return result_dict

    last_backups = None
    last_paramet = None

    while reg:
        if last_backups is None:
            paramet = input(str("[+] Введите свой параметр для генерации списка файлов бэкапов: "))
            backups_files = gpt_backups(detected_cms, paramet)
        else:
            print(Bcolors.OKCYAN + '[+]: ' + "Хотите продолжить с предыдущим запросом? [yes/new]")
            choice = input(str("Ответ: "))
            if choice.lower() == "yes":
                backups_files = last_backups
                paramet = input(
                    str("[+] Введите свой параметр для генерации списка файлов бэкапов (оставьте пустым для использования предыдущего запроса): "))
                if paramet == "":
                    paramet = last_paramet
            else:
                paramet = input(str("[+] Введите свой параметр для генерации списка файлов бэкапов: "))
                backups_files = gpt_backups(detected_cms, paramet)

        last_backups = backups_files
        last_paramet = paramet

        results_backups = check_files(backups_files, link, headers, cookies)

        if txtman:
            name = input(str("Введите имя для файла: "))
            with open(f"{name}.txt", "w") as f:
                for result in results_backups:
                    f.write(result)
                f.close()
                print(f"File name {name}.txt was created in {os.getcwd()} ")
        else:
            for result in results_backups:
                print(result)

        print(Bcolors.OKCYAN + "[?]: " + "ПОПРОБОВАТЬ СНОВА ?[Yes/no]")
        usl = input(str("Ответ: "))
        if usl.lower() == "yes":
            continue
        else:
            break


def check_subdomains(dictionary_dir, link, headers, cookies):
    directories = []
    print(Bcolors.OKCYAN + "[+]: " + "ИДЁТ ПРОВЕРКА")
    with alive_bar(len(dictionary_dir)) as bar:
        for key, subdom in dictionary_dir.items():
            url = urlunsplit(('https', f"{subdom}.{urlsplit(link).hostname}", '', '', ''))
            try:
                response = requests.get(url, headers=headers, cookies=cookies)
                if response.status_code == 200:
                    directories.append(f"{Bcolors.OKGREEN}[+]{Bcolors.ENDC} {key}: {url}")
                    if args1.response:
                        print(Bcolors.OKCYAN + "[+]" + "[response]" + "Http-code:\n")
                        print(response.text)
                        print(Bcolors.OKCYAN + "[+]" + "[response]" + f"Cookies:\n")
                        print(response.cookies)
                else:
                    directories.append(f"{Bcolors.FAIL}[-]{Bcolors.ENDC} {key}: {url}")
            except requests.exceptions.ConnectionError as e:
                directories.append(f"{Bcolors.FAIL}[-]{Bcolors.ENDC} {key}: {url} ({e})")
            bar()
    return directories


def subdomains():
    print(Bcolors.OKGREEN + "[+]: " + "CHECK SUBDOMAINS")

    reg = True
    last_subdomains = None
    last_paramet = None

    def gpt_subdomains(paramet=""):
        nonlocal last_paramet

        if paramet == "":
            print(
                Bcolors.OKCYAN + '[+]: ' + "Введите свой параметр для генерации словаря субдоменов через chatgpt или напишите 'default': ")
        else:
            print(Bcolors.OKCYAN + f'[+]: Используется заданный параметр: {paramet}')

        print(
            Bcolors.OKCYAN + '[TYPE]: ' + "Используйте ' - как знак ковычки. Не пишите сюда jailbreak")

        if paramet == "default":
            paramet = f"Сгенерируй пожалуйста большой список субдоменов для , которые ты знаешь.\n"
        elif paramet == "":
            paramet = input(str("param: "))

        desc = "Этот список будет использоваться для поиска субдоменов на сайте."
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=(
                f"{desc}{paramet}.Просто выведи список субдоменов без своих пояснений.\n"
            ),
            temperature=temp,
            max_tokens=2048,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop=["\n\n"],
        )

        status = response.choices[0].text.split('\n')

        result_dict = {}
        for i, item in enumerate(status):
            if item.strip():
                result_dict[i] = '/'.join([s.strip() for s in item.split('/')]).replace('//', '/')

        print(Bcolors.OKCYAN + "[+]: " + "СЛОВАРЬ СУБДОМЕНОВ ГОТОВ")

        last_paramet = paramet
        return result_dict

    while reg:
        if last_subdomains is None:
            subdomains_dict = gpt_subdomains()
        else:
            print(Bcolors.OKCYAN + '[+]: ' + "Хотите продолжить с предыдущим запросом? [yes/new]")
            choice = input(str("Ответ: "))
            if choice.lower() == "yes":
                subdomains_dict = last_subdomains
                paramet = input(
                    str("[+] Введите свой параметр для генерации списка субдоменов (оставьте пустым для использования предыдущего запроса): "))
                if paramet == "":
                    paramet = last_paramet
            else:
                paramet = input(str("[+] Введите свой параметр для генерации списка субдоменов: "))
                subdomains_dict = gpt_subdomains(paramet)

        last_subdomains = subdomains_dict

        results = check_subdomains(subdomains_dict, link, headers, cookies)

        if txtman:
            name = input(str("Введите имя для файла: "))
            with open(f"{name}.txt", "w") as f:
                for result in results:
                    f.write(result)
                f.close()
                print(f"File name {name}.txt was created in {os.getcwd()} ")
                if txtman:
                    name = input(str("Введите имя для файла: "))
                    with open(f"{name}.txt", "w") as f:
                        for result in results:
                            f.write(result)
                        f.close()
                        print(f"File name {name}.txt was created in {os.getcwd()} ")
                else:
                    for result in results:
                        print(result)

                print(Bcolors.OKCYAN + "[?]: " + "ПОПРОБОВАТЬ СНОВА ?[Yes/no]")
                usl = input(str("Ответ: "))
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
        subdomains()
    if args1.insecure:
        insecure(detected_cms)
    if args1.api_enum:
        url = link
        api_enumeration(url, api_key, temp, headers, cookies, args1.response)
    if args1.crawler:
        url = link
        web_crawler(url, api_key, temp, headers, cookies, args1.response)
