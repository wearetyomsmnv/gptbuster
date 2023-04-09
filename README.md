# gptbuster
Webdir fuzzer based on ChatGPT



# Usage

```
git clone https://github.com/wearetyomsmnv/gptbuster
```
```
cd gptbuster
```
```
pip3 install -r requirements
```
```
python3 main.py -h 
```


python3 main.py <website> <api-key>

ex: python3 main.py https://google.com/ sk*********** 0.12 <args>


# Docker

```
docker build -t gptbuster . 
```

ex: sudo docker run -it <image_name> https://google.com/ sk*********** 0.12 <args>



### Options


```
Основные параметры

positional arguments:
  link          Укажите ссылку на веб-ресурс
  api_key       Укажите api-key для chat-gpt
  temperature   Укажите температуру для параметров [от 0.00 до 1.00]

options:
  -h, --help    show this help message and exit
  --insecure    Поиск небезопасных директорий
  --backup      Поиск бекапов
  --subdomains  Перечисление субдоменов
  --api_enum    Фаззинг по апи
  --crawler     Black-box crawler
  --output      .txt output
```

# PS

Наслаждайся. В скором времени будут добавлены крутые фичи! :joy:

# КАКИЕ ПРОБЛЕМЫ СУЩЕСТВУЮТ

GPT - это генеративная нейросеть и порой данные, которые получаем мы при запросе - имеют много мусора и неточностей. Это приводит к фактору непредсказуемости при использовании данных. Возможно со временем удастся изобрести универсальный промпт
