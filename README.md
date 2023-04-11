# gptbuster
Webdir fuzzer based on ChatGPT


# Why gptbuster is needed ?

gptbuster is designed to solve the problem when we do not have a dictionary - we need to look up directories, files or parameters on a site. The special feature is that gptbuster works with chatgpt and any user can create a dictionary of any complexity as quickly as possible. Whether it's multi-level, masked or parameterized or both, so that with partial or no data about what might be on the site, it is possible to list it for further development in a pentest. 


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

Go to the project folder
```
cd gptbuster
```

Creating a virtual environment
```
python3 -m venv gptbuster_venv
```

or

```
virtualenv gptbuster_venv
```


We then need to activate the virtual environment

### Linux:
```
 source gptbuster_venv/bin/activate
```

### Windows:

```
 gptbuster_venv\Scripts\activate
```


And put dependencies into it

```
 pip3 install -r requirements.txt
```



## Options


```
GPT-based web-dir fuzzer, crawler
@wearetyomsmnv
web fuzzing,crawling,enumerator for penetration testers with <3

usage: main.py [-h] [--insecure] [--backup] [--subdomains] [--api_enum] [--crawler] [--output] [--cookies [COOKIES]]
               [--response] [--headers] [--head] [--r [R]] [--x [X]] [--proxy]
               link api_key temperature

Basic parameters

positional arguments:
  link                 Provide a link to a web resource
  api_key              Specify the api-key for chat-gpt
  temperature          Specify the temperature for parameters [0.00 to 1.00]

options:
  -h, --help           show this help message and exit
  --insecure           Search for unsafe directories
  --backup             Searching for backups
  --subdomains         Listing of subdomains
  --api_enum           Fuzzing by api
  --crawler            Black-box crawler
  --output             .txt output
  --cookies [COOKIES]  Add self cookies for request
  --response           View responses for all requests
  --headers            View headers for all requests
  --head               Add custom headers in request head
  --r [R]              Add your request file
  --x [X]              Change default http method (get, post, put, delete)
  --proxy              Use proxy for requests


```

# PS

Enjoy. Cool features will be added soon! :joy:

# Problems you may encounter.

GPT is a generative neural network and sometimes the data we receive when we query it has a lot of rubbish and inaccuracies. This leads to the unpredictability factor when using the data. Perhaps in time a universal prompt can be invented.
