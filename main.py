import openai
import requests
import signal
from pyfiglet import figlet_format
import argparse
from bs4 import BeautifulSoup
import sys
from termcolor import cprint
from alive_progress import alive_bar


class Bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def signal_handler(sig, frame):
    print("\nПрограмма завершена пользователем.")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


def print_banner():
    print()
    cprint(figlet_format('GPTBUSTER', font='starwars', width=200),
           'yellow', attrs=['bold'])


print_banner()

print(Bcolors.HEADER + 'build 1.1.0')
print(Bcolors.HEADER + 'GPT-based web-dir fuzzer')
print(Bcolors.HEADER + '@wearetyomsmnv')
print(Bcolors.OKGREEN + 'for web penetration testers with <3')


print(Bcolors.FAIL)
commands = argparse.ArgumentParser(description='GPT-based directory fuzzer')
commands.add_argument('link', help='Укажите ссылку на веб-ресурс')
commands.add_argument('api_key', help='Укажите api-key для chat-gpt')
commands.add_argument('num', help='Укажите колличество слов для словаря[1-50](Не всегда отрабатывает)')
commands.add_argument('--insecure', action='store_true', help='поиск небезопасных директорий')
commands.add_argument('--backup', action='store_true', help='поиск бекапов')


args1 = commands.parse_args()

link = args1.link
api_key = args1.api_key
insecure = args1.insecure
backups = args1.backup
num = args1.num




if not any([link, api_key]):
    print(Bcolors.FAIL + "[FAIL:] " + 'Вы не выбрали аргументы')
    print(Bcolors.FAIL + "[NOTE:] " + 'Попробуйте ещё раз')
    sys.exit()

openai.api_key = api_key

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


detected_cms = detect_cms(link)
print(Bcolors.OKGREEN + f"Detected CMS: {detected_cms}")


def gpt(cms):

    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=(
            f"Сгенерируй пожалуйста большой список директорий и файлов для CMS {cms}, которые ты знаешь. "
            f"Просто выведи список директорий без своих пояснений.\n"
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

directories_dict = gpt(detected_cms)

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




results = check_files(directories_dict, link)
for result in results:
    print(result)

if insecure:
    print(Bcolors.OKGREEN + "[+]: "+"CHECK INSECURE DIR")


    def gpt_insecure(cms):

        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=(
                f"Сгенерируй пожалуйста большой список небезопасных директорий и небезопасных файлов для CMS {cms}, которые ты знаешь. "
                f"Просто выведи список директорий без своих пояснений.\n"
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


    directories_dict = gpt_insecure(detected_cms)

    results_insecure = check_files(directories_dict, link)
    for result in results_insecure:
        print(result)

if backups:
    print(Bcolors.OKGREEN + "[+]: "+"CHECK BACKUP FILES")


    def gpt_insecure(cms):

        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=(
                f"Сгенерируй пожалуйста большой список файлов, которые могут являться бэкапами для CMS {cms},"
                f" которые ты знаешь. "
                f"Просто выведи список директорий без своих пояснений.\n"
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


    directories_dict = gpt_insecure(detected_cms)

    results_backups = check_files(directories_dict, link)
    for result in results_backups:
        print(result)