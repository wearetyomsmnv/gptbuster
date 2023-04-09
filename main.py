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

print(Bcolors.HEADER + 'build 1.3.3')
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

if not any([link, api_key, temp]):
    print(Bcolors.FAIL + "[FAIL:] " + 'Вы не указали основные аргументы')
    print(Bcolors.FAIL + "[NOTE:] " + 'Попробуйте ещё раз')
    sys.exit()

if not any([insecure, backups, subdomains,
            api_enumeration, crawler, output, cookies, basic_auth, b64]):
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


cookies = {'Cookie': args1.cookies} if args1.cookies else {}
headers = {'Authorization': args1.basic_auth} if args1.basic_auth else {}




def check_files(dictionary_dir, link):
    directories = []
    print(Bcolors.OKCYAN + "[+]: " + "ИДЁТ ПРОВЕРКА")
    with alive_bar(len(dictionary_dir)) as bar:
        for key, directory in dictionary_dir.items():
            url = f"{link.lstrip('/')}{directory}"
            response = requests.get(url, headers=headers, cookies=cookies)
            if response.status_code == 200:
                directories.append(f"{Bcolors.OKGREEN}[+]{Bcolors.ENDC} {key}: {url}")
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


results = check_files(directories_dict, link)
for result in results:
    print(result)


def check_wordpress(linked):
    response = requests.get(f"{linked}wp-login.php", headers=headers, cookies=cookies)
    if response.status_code == 200:
        return True

    response = requests.get(f"{linked}wp-includes/", headers=headers, cookies=cookies)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        if soup.find("meta", {"name": "generator", "content": "WordPress"}):
            return True

    return False


def check_woocommerce(link):
    response = requests.get(link, headers=headers, cookies=cookies)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        if soup.find("meta", {"name": "generator", "content": "WooCommerce"}):
            return True

    return False


def check_joomla(linked):
    response = requests.get(f"{linked}administrator/", headers=headers, cookies=cookies)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        if soup.find("meta", {"name": "generator", "content": "Joomla!"}):
            return True

    response = requests.get(f"{linked}templates/", headers=headers, cookies=cookies)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        if soup.find("meta", {"name": "generator", "content": "Joomla!"}):
            return True

    response = requests.get(f"{linked}components/", headers=headers, cookies=cookies)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        if soup.find("meta", {"name": "generator", "content": "Joomla!"}):
            return True

    return False


def check_drupal(linked):
    response = requests.get(f"{linked}modules/", headers=headers, cookies=cookies)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        if soup.find("meta", {"name": "generator", "content": "Drupal"}):
            return True

    return False


def check_shopify(link):
    response = requests.get(link, headers=headers, cookies=cookies)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        if soup.find("meta", {"name": "generator", "content": "Shopify"}):
            return True

    return False


def check_1c_bitrix(linked):
    response = requests.get(f"{linked}bitrix/", headers=headers, cookies=cookies)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        if soup.find("meta", {"name": "generator", "content": "1C-Bitrix"}):
            return True

    return False


def detect_cms(link):
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


detected_cms = detect_cms(link)
print(Bcolors.OKGREEN + f"Detected CMS: {detected_cms}")


def insecure(detected_cms):
    print(Bcolors.OKGREEN + "[+]: " + "CHECK INSECURE DIR")

    reg = True

    def gpt_insecure(cms):

        desc = "Этот список будет использоваться для поиска небезопасных директорий и параметров"
        print(
            Bcolors.OKCYAN + '[+]: ' + "Введите свой параметр для генерации словаря через chatgpt или напишите 'default': ")
        print(
            Bcolors.OKCYAN + '[TYPE]: ' + "Используйте ' - как знак ковычки. Не пишите сюда jailbreak")

        parametr = input(str("param: "))
        if parametr == "default":
            paramet = f"Сгенерируй пожалуйста большой список небезопасных директорий и параметров для {cms}, которые ты знаешь.Просто выведи список директорий без своих пояснений.\n"
        else:
            paramet = parametr

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

    while reg:
        directories_dict = gpt_insecure(detected_cms)

        results_insecure = check_files(directories_dict, link)

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

    def gpt_backups(cms):

        print(
            Bcolors.OKCYAN + '[+]: ' + "Введите свой параметр для генерации словаря api через chatgpt или напишите 'default': ")
        print(
            Bcolors.OKCYAN + '[TYPE]: ' + "Используйте ' - как знак ковычки. Не пишите сюда jailbreak")
        parametr = input(str("param: "))
        if parametr == "default":
            paramet = f"Сгенерируй пожалуйста большой список файлов, которые могут являться бэкапами для {cms}, которые ты знаешь.\n"
        else:
            paramet = parametr

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

    while reg:
        directories_dict = gpt_backups(detected_cms)

        results_backups = check_files(directories_dict, link)

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


def check_subdomains(dictionary_dir, link):
    directories = []
    print(Bcolors.OKCYAN + "[+]: " + "ИДЁТ ПРОВЕРКА")
    with alive_bar(len(dictionary_dir)) as bar:
        for key, subdom in dictionary_dir.items():
            url = urlunsplit(('https', f"{subdom}.{urlsplit(link).hostname}", '', '', ''))
            try:
                response = requests.get(url, headers=headers, cookies=cookies)
                if response.status_code == 200:
                    directories.append(f"{Bcolors.OKGREEN}[+]{Bcolors.ENDC} {key}: {url}")
                else:
                    directories.append(f"{Bcolors.FAIL}[-]{Bcolors.ENDC} {key}: {url}")
            except requests.exceptions.ConnectionError as e:
                directories.append(f"{Bcolors.FAIL}[-]{Bcolors.ENDC} {key}: {url} ({e})")
            bar()
    return directories


def subdomains():
    print(Bcolors.OKGREEN + "[+]: " + "CHECK SUBDOMAINS")

    reg = True

    def gpt_subdomains():

        print(
            Bcolors.OKCYAN + '[+]: ' + "Введите свой параметр для генерации словаря api через chatgpt или напишите 'default': ")
        print(
            Bcolors.OKCYAN + '[TYPE]: ' + "Используйте ' - как знак ковычки. Не пишите сюда jailbreak")
        parametr = input(str("param: "))
        if parametr == "default":
            paramet = f"Сгенерируй пожалуйста большой список субдоменов для , которые ты знаешь.\n"
        else:
            paramet = parametr
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

        return result_dict

    while reg:
        directories_dict = gpt_subdomains()
        results = check_subdomains(directories_dict, link)

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
        api_enumeration(url, api_key, temp, headers, cookies)
    if args1.crawler:
        url = link
        web_crawler(url, api_key, temp, headers, cookies)
