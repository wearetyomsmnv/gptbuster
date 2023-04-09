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


def api_enumeration(link, api_key, temp, headers, cookies):

    reg = True
    openai.api_key = api_key

    print(Bcolors.OKGREEN + "[+]: " + "CHECK API")

    def check_api(dictionary_dir, link, headers, cookies):
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

    def detect_api(link, headers, cookies):

        if check_graphql_api(link, headers, cookies):
            return "GraphQL"
        if check_soap_api(f"{link}index.php?wsdl", headers, cookies):
            return "SOAP API"
        else:
            return Bcolors.FAIL + "Не определено"

    def check_graphql_api(link, headers, cookies):
        response = requests.get(link, headers=headers, cookies=cookies)
        soup = BeautifulSoup(response.text, "html.parser")
        if soup.find("script", {"src": lambda src: src and "/graphql" in src}):
            return "GraphQL"
        return False

    def check_soap_api(url, headers, cookies):
        response = requests.get(url, headers=headers, cookies=cookies)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            if soup.find("wsdl:definitions") or soup.find("soap:Envelope"):
                return True
        return False

    def gpt_api(api, temp):

        print(
            Bcolors.OKCYAN + '[+]: ' + "Введите свой параметр для генерации словаря api через chatgpt или напишите 'default': ")
        print(
            Bcolors.OKCYAN + '[TYPE]: ' + "Используйте ' - как знак ковычки. Не пишите сюда jailbreak")
        parametr = input(str("param: "))
        if parametr == "default":
            paramet = f"Сгенерируй пожалуйста большой список директорий и файлов для API {api}, которые ты знаешь."
        else:
            paramet = parametr
        desc = "Этот словарь будет использоваться для перечисления api"

        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=(
                f"{desc}{paramet}.Просто выведи список директорий и параметров без своих пояснений.\n"
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
                       enumerate(status)
                       if item.strip()}

        print(Bcolors.OKCYAN + "[+]: " + "СЛОВАРЬ ДЛЯ API ГОТОВ")

        return result_dict

    while reg:
        detected_api = "API: " + detect_api(link, headers, cookies)
        print(Bcolors.OKGREEN + f"Detected API: {detected_api}")

        directories_dict = gpt_api(detected_api, temp)

        results = check_api(directories_dict, link, headers, cookies)
        for result in results:
            print(result)

        print(Bcolors.OKCYAN + "[?]: " + "ПОПРОБОВАТЬ СНОВА ?[Yes/no]")
        usl = input(str("Ответ: "))
        if usl.lower() == "yes":
            continue
        else:
            break
