# gptbuster
Webdir fuzzer based on ChatGPT

# USAGE


git clone https://github.com/wearetyomsmnv/gptbuster

cd gptbuster

pip3 install -r requirements

python3 main.py <website> <api-key>


ex: python3 main.py https://google.com/ sk***********

# ЧТО МОЖЕТ УЖЕ

Поддержка следующих cms:
Bitrix
Wordpress
Joomla
Drupal
WooCommerce
Shopify

Поиск небезопасных директорий по сгенерированному словарю (--insecure)

Поиск бекапов также по сгенерированному словарю (--backup)

Наслаждайся. В скором времени будут добавлены крутые фичи! :joy:

# КАКИЕ ПРОБЛЕМЫ СУЩЕСТВУЮТ

GPT - это генеративная нейросеть и порой данные, которые получаем мы при запросе - имеют много мусора и неточностей. С каждым коммитом происходят изменения - в алгоритме преобразования данных в словарь. Чтобы по итогу данные могли адекватно отправляться с запросом.
