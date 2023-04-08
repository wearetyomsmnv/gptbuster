# gptbuster
Webdir fuzzer based on ChatGPT

# USAGE


git clone https://github.com/wearetyomsmnv/gptbuster

cd gptbuster

pip3 install -r requirements

python3 main.py -h 


python3 main.py <website> <api-key>

# Docker

docker build -t gptbuster . 

docker run -it <container name> <args> 


ex: python3 main.py https://google.com/ sk*********** --other

# ЧТО МОЖЕТ УЖЕ

Поддержка следующих cms:
Bitrix,
Wordpress,
Joomla,
Drupal,
WooCommerce,
Shopify.

- Перечисление субдоменов (--subdomains)
 
- Поиск небезопасных директорий по сгенерированному словарю (--insecure)

- Поиск бекапов также по сгенерированному словарю (--backup)

- Перечисление api (--api_enum)

- Добавлен кравлинг (--crawl)

# PS

Наслаждайся. В скором времени будут добавлены крутые фичи! :joy:

# КАКИЕ ПРОБЛЕМЫ СУЩЕСТВУЮТ

GPT - это генеративная нейросеть и порой данные, которые получаем мы при запросе - имеют много мусора и неточностей. Это приводит к фактору непредсказуемости при использовании данных. Возможно со временем удастся изобрести универсальный промпт
