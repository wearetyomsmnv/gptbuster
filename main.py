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

print(Bcolors.HEADER + 'build 1.3.1')
print(Bcolors.HEADER + 'GPT-based web-dir fuzzer, crawler')
print(Bcolors.HEADER + '@wearetyomsmnv')
print(Bcolors.OKGREEN + 'web fuzzer for penetration testers with <3')


print(Bcolors.FAIL)
commands = argparse.ArgumentParser(description='GPT-based directory fuzz and crawling')
commands.add_argument('link', help='Укажите ссылку на веб-ресурс')
commands.add_argument('api_key', help='Укажите api-key для chat-gpt')
commands.add_argument('--insecure', action='store_true', help='Поиск небезопасных директорий')
commands.add_argument('--backup', action='store_true', help='Поиск бекапов')
commands.add_argument('--subdomains', action='store_true', help='Перечисление субдоменов')
commands.add_argument('--api_enum', action='store_true', help='Фаззинг по апи')
commands.add_argument('--crawler', action='store_true', help='Black-box crawler')
commands.add_argument('--output', action='store_true', default=False, help='.txt output')


args1 = commands.parse_args()

link = args1.link
api_key = args1.api_key
insecure = args1.insecure
backups = args1.backup
subdomains = args1.subdomains
api_enum = args1.api_enum
crawler = args1.crawler
output = args1.output


if not any([link, api_key]):
    print(Bcolors.FAIL + "[FAIL:] " + 'Вы не указали основные аргументы')
    print(Bcolors.FAIL + "[NOTE:] " + 'Попробуйте ещё раз')
    sys.exit()

if not any([insecure, backups, subdomains,
            api_enumeration, crawler, output]):
    print(Bcolors.FAIL + "[FAIL:] " + 'Вы не указали дополнительные аргументы')
    print(Bcolors.FAIL + "[NOTE:] " + 'Попробуйте ещё раз')
    sys.exit()

openai.api_key = api_key

directories_dict = {}
directories_dict2 = {}
detected_cms = ""
detected_api = ""
txtman = ""

def check_files(dictionary_dir, link):
    directories = []
    print(Bcolors.OKCYAN + "[+]: "+"ИДЁТ ПРОВЕРКА")
    with alive_bar(len(dictionary_dir)) as bar:
        for key, directory in dictionary_dir.items():
            url = f"{link.lstrip('/')}{directory}"
            response = requests.get(url)
            if response.status_code == 200:
                directories.append(f"{Bcolors.OKGREEN}[+]{Bcolors.ENDC} {key}: {url}")
            else:
                directories.append(f"{Bcolors.FAIL}[-]{Bcolors.ENDC} {key}: {url}")
            bar()
    return directories


def gpt(cms):

    print(Bcolors.OKCYAN + '[+]: ' + "Введите свой параметр для генерации словаря через chatgpt или напишите 'default': ")
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
        temperature=0.5,
        max_tokens=2048,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=["\n\n"],
    )

    status = response.choices[0].text.split('\n')

    result_dict = {i: '/'.join([s.strip() for s in item.split('/')]).replace('//', '/') for i, item in enumerate(status)if item.strip()}

    print(Bcolors.OKCYAN + "[+]: " + "СЛОВАРЬ ГОТОВ")

    return result_dict


results = check_files(directories_dict, link)
for result in results:
    print(result)


def check_wordpress(linked):
    response = requests.get(f"{linked}wp-login.php")
    if response.status_code == 200:
        return True

    response = requests.get(f"{linked}wp-includes/")
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        if soup.find("meta", {"name": "generator", "content": "WordPress"}):
            return True

    return False


def check_woocommerce(linked):
    response = requests.get(linked)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        if soup.find("meta", {"name": "generator", "content": "WooCommerce"}):
            return True

    return False


def check_joomla(linked):
    response = requests.get(f"{linked}administrator/")
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        if soup.find("meta", {"name": "generator", "content": "Joomla!"}):
            return True

    response = requests.get(f"{linked}templates/")
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        if soup.find("meta", {"name": "generator", "content": "Joomla!"}):
            return True

    response = requests.get(f"{linked}components/")
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        if soup.find("meta", {"name": "generator", "content": "Joomla!"}):
            return True

    return False


def check_drupal(linked):
    response = requests.get(f"{linked}modules/")
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        if soup.find("meta", {"name": "generator", "content": "Drupal"}):
            return True

    return False


def check_shopify(linked):
    response = requests.get(linked)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        if soup.find("meta", {"name": "generator", "content": "Shopify"}):
            return True

    return False


def check_1c_bitrix(linked):
    response = requests.get(f"{linked}bitrix/")
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        if soup.find("meta", {"name": "generator", "content": "1C-Bitrix"}):
            return True

    return False


def detect_cms(linked):
    response = requests.get(linked)
    soup = BeautifulSoup(response.text, "html.parser")

        # Check for WordPress
    if soup.find("meta", {"name": "generator", "content": "WordPress"}) or \
        soup.find_all("link", rel="stylesheet", href=lambda href: href and "wp-content" in href) or \
        soup.find("script", {"id": "wp-emoji-release"}):
        return "WordPress"

        # Check for WooCommerce
    if soup.find("meta", {"name": "generator", "content": "WooCommerce"}) or \
        soup.find_all("link", rel="stylesheet", href=lambda href: href and "woocommerce" in href) or \
        soup.find("script", {"src": lambda src: src and "woocommerce" in src}):
        return "WooCommerce"

        # Check for shopify
    if soup.find("meta", {"name": "generator", "content": "Shopify"}) or \
        soup.find_all("link", rel="stylesheet", href=lambda href: href and "shopify" in href) or \
        soup.find("script", {"src": lambda src: src and "shopify" in src}):
        return "Shopify"

        # Check for Joomla
    elif soup.find("meta", {"name": "generator", "content": "Joomla!"}) or \
        soup.find_all("link", rel="stylesheet", href=lambda href: href and "joomla" in href) or \
        soup.title and "Joomla!" in soup.title.string:
        return "Joomla"

        # Check for Drupal
    elif soup.find("meta", {"name": "generator", "content": "Drupal"}):
        return "Drupal"

        # Check for 1C-Bitrix
    elif soup.find("meta", {"name": "generator", "content": "1C-Bitrix"}) or \
        soup.find_all("link", rel="stylesheet", href=lambda href: href and "bitrix" in href):
        return "1C-Bitrix"

    else:
        return "CMS не определена"


detected_cms = "Для CMS: " + detect_cms(link)
print(Bcolors.OKGREEN + f"Detected CMS: {detected_cms}")


def insecure(detected_cms):
    print(Bcolors.OKGREEN + "[+]: "+"CHECK INSECURE DIR")

    reg = True
    def gpt_insecure(cms):

        print(Bcolors.OKCYAN + '[+]: ' + "Введите свой параметр для генерации словаря через chatgpt или напишите 'default': ")
        parametr = input(str("param: "))
        if parametr == "default":
            paramet = f"Сгенерируй пожалуйста большой список небезопасных директорий и небезопасных файлов для {cms}, которые ты знаешь.Просто выведи список директорий без своих пояснений.\n"
        else:
            paramet = parametr

        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=(
                f"{paramet}.Просто выведи список директорий без своих пояснений.\n"
            ),
            temperature=0.5,
            max_tokens=2048,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop=["\n\n"],
        )

        status = response.choices[0].text.split('\n')

        result_dict = {i: '/'.join([s.strip() for s in item.split('/')]).replace('//', '/') for i, item in enumerate(status) if item.strip()}

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

    print(Bcolors.OKGREEN + "[+]: "+"CHECK BACKUP FILES")

    def gpt_backups(cms):

        print(
            Bcolors.OKCYAN + '[+]: ' + "Введите свой параметр для генерации словаря api через chatgpt или напишите 'default': ")
        parametr = input(str("param: "))
        if parametr == "default":
            paramet = f"Сгенерируй пожалуйста большой список файлов, которые могут являться бэкапами для {cms}, которые ты знаешь.\n"
        else:
            paramet = parametr

        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=(
                f"{paramet}.Просто выведи список директорий без своих пояснений.\n"
            ),
            temperature=0.5,
            max_tokens=2048,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop=["\n\n"],
        )

        status = response.choices[0].text.split('\n')

        result_dict = {i: '/'.join([s.strip() for s in item.split('/')]).replace('//', '/') for i, item in enumerate(status) if item.strip()}

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
    print(Bcolors.OKCYAN + "[+]: "+"ИДЁТ ПРОВЕРКА")
    with alive_bar(len(dictionary_dir)) as bar:
        for key, directory in dictionary_dir.items():
            url = f"https://{directory}.{link.lstrip('https://')}/"
            response = requests.get(url)
            if response.status_code == 200:
                directories.append(f"{Bcolors.OKGREEN}[+]{Bcolors.ENDC} {key}: {url}")
            else:
                directories.append(f"{Bcolors.FAIL}[-]{Bcolors.ENDC} {key}: {url}")
            bar()
    return directories


def subdomains(detected_cms):
    print(Bcolors.OKGREEN + "[+]: "+"CHECK SUBDOMAINS")

    reg = True
    def gpt_subdomains(cms):

        global paramet
        print(
            Bcolors.OKCYAN + '[+]: ' + "Введите свой параметр для генерации словаря api через chatgpt или напишите 'default': ")
        parametr = input(str("param: "))
        if parametr == "default":
            paramet = f"Сгенерируй пожалуйста большой список субдоменов для {cms}, которые ты знаешь.\n"
        else:
            paramet = parametr

        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=(
                f"{paramet}.Просто выведи список субдоменов без своих пояснений.\n"
            ),
            temperature=0.5,
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
        directories_dict = gpt_subdomains(detected_cms)
        results = check_files(directories_dict, link)

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
        subdomains(detected_cms)
    if args1.insecure:
        insecure(detected_cms)
    if args1.api_enum:
        url = link
        api_enumeration(url, api_key)
    if args1.crawler:
        url = link
        web_crawler(url, api_key)
