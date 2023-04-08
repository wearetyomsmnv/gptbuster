from sc.colors import Bcolors
from alive_progress import alive_bar
import requests
from bs4 import BeautifulSoup
import openai
import signal
import sys


def signal_handler(sig, frame):
    print("\nПрограмма завершена пользователем.")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


def api_enumeration(link, api_key):

    reg = True
    openai.api_key = api_key

    print(Bcolors.OKGREEN + "[+]: " + "CHECK API")

    def check_api(dictionary_dir, link):
        directories = []
        print(Bcolors.OKCYAN + "[+]: " + "ИДЁТ ПРОВЕРКА")
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

    def detect_api(link):

        if check_graphql_api(link):
            return "GraphQL"
        if check_soap_api(f"{link}index.php?wsdl"):
            return "SOAP API"
        else:
            return "API не определён"

    def check_graphql_api(link):
        response = requests.get(link)
        soup = BeautifulSoup(response.text, "html.parser")
        if soup.find("script", {"src": lambda src: src and "/graphql" in src}):
            return "GraphQL"
        return False

    def check_soap_api(url):
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            if soup.find("wsdl:definitions") or soup.find("soap:Envelope"):
                return True
        return False

    def gpt(api):

        global paramet
        print(
            Bcolors.OKCYAN + '[+]: ' + "Введите свой параметр для генерации словаря api через chatgpt или напишите 'default': ")
        parametr = input(str("param: "))
        if parametr == "default":
            paramet = f"Сгенерируй пожалуйста большой список директорий и файлов для API {api}, которые ты знаешь."
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

        result_dict = {i: '/'.join([s.strip() for s in item.split('/')]).replace('//', '/') for i, item in
                       enumerate(status)
                       if item.strip()}

        print(Bcolors.OKCYAN + "[+]: " + "СЛОВАРЬ ДЛЯ API ГОТОВ")

        return result_dict

    while reg:
        detected_api = "API: " + detect_api(link)
        print(Bcolors.OKGREEN + f"Detected API: {detected_api}")

        directories_dict = gpt(detected_api)

        results = check_api(directories_dict, link)
        for result in results:
            print(result)

        print(Bcolors.OKCYAN + "[?]: " + "ПОПРОБОВАТЬ СНОВА ?[Yes/no]")
        usl = input(str("Ответ: "))
        if usl.lower() == "yes":
            continue
        else:
            break
