# gptbuster
Webdir fuzzer based on ChatGPT


# Зачем вообще gptbuster ?

gptbuster - призван решить проблему, когда не имея словаря - нам нужно просмотреть директории, файлы или параметры на сайте. Особенность в том, что gptbuster работает с chatgpt и любой пользователь может максимально быстро создать словарь любой сложности. Будь то многоуровневый, по маске или с параметрами или всё вместе для того чтобы имея частичные данные о том, что может быть на сайте вообще или вовсе не располагая данными - можно было провести перечисление для дальнейшего развития при пентесте. 


[![1.png](https://i.postimg.cc/fT3QVTpN/1.png)](https://postimg.cc/8jV03DTK)


[![image-2.jpg](https://i.postimg.cc/W4jWtC7T/image-2.jpg)](https://postimg.cc/TK7q4kS4)



# Usage

```
git clone https://github.com/wearetyomsmnv/gptbuster
```
```
cd gptbuster
```
```
pip3 install -r requirements.txt
```

```
example: python3 main.py https://google.com/ sk*********** 0.12 --subdomains
```


# Docker

```
docker build -t gptbuster . 
```

```
example: sudo docker run -it <image_name> https://google.com/ sk*********** 0.12 --subdomains
```


# python venv

Переходим в папку с проектом
```
cd gptbuster
```

Создаём виртуальное окружение
```
python3 -m venv gptbuster_venv
```

или

```
virtualenv gptbuster_venv
```


После чего нам необходимо активировать виртуальное окружение

### Linux:
```
 source gptbuster_venv/bin/activate
```

### Windows:

```
 gptbuster_venv\Scripts\activate
```


И устанавливаем в него зависимости

```
 pip3 install -r requirements.txt
```



## Options


```
GPT-based web-dir fuzzer, crawler
@wearetyomsmnv
web fuzzing,crawling,enumerator for penetration testers with <3

usage: main.py [-h] [--insecure] [--backup] [--subdomains] [--api_enum] [--crawler] [--output] [--cookies [COOKIES]] [--response] [--headers] [--head]
               [--r [R]]
               link api_key temperature

Основные параметры

positional arguments:
  link                 Укажите ссылку на веб-ресурс
  api_key              Укажите api-key для chat-gpt
  temperature          Укажите температуру для параметров [от 0.00 до 1.00]

options:
  -h, --help           show this help message and exit
  --insecure           Поиск небезопасных директорий
  --backup             Поиск бекапов
  --subdomains         Перечисление субдоменов
  --api_enum           Фаззинг по апи
  --crawler            Black-box crawler
  --output             .txt output
  --cookies [COOKIES]  Add self cookies for request
  --response           View responses for all requests
  --headers            View headers for all requests
  --head               Add custom headers in request head
  --r [R]              Add your request file


```

# PS

Наслаждайся. В скором времени будут добавлены крутые фичи! :joy:

# Проблемы с которыми можно столкнуться.

GPT - это генеративная нейросеть и порой данные, которые получаем мы при запросе - имеют много мусора и неточностей. Это приводит к фактору непредсказуемости при использовании данных. Возможно со временем удастся изобрести универсальный промпт
