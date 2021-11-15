import os
import time
from art import *

import random
import string as st
import datetime as dt
from enum import Enum
from typing import Dict, Optional
import urllib.request
import json
import httpx
from apiclient import APIClient, Get, endpoint
import os
import time
import colorama
import math
import asciify
import colorize

def rgb_to_hex(rgb):
	return '%02x%02x%02x' % rgb

# import image stuff
from PIL import Image
import urllib3
http = urllib3.PoolManager()
import io

# load images
def loadFromUrl(URL, columns=60, color=True):
	fd = http.request('GET', URL)
	image_file = io.BytesIO(fd.data)
	im = Image.open(image_file)

	size = im.size
	rows = columns * size[1] / size[0]
	rows = int(round(rows))
	"""
	rows/columns = height/width
	"""
	im = im.resize((columns, rows))
	px = im.load()
	size = im.size
	output = ""
	for y in range(0, size[1]):
		for x in range(0, size[0]):
			_px = px[x,y]
			_a = asciify.getRawChar(_px[0], _px[1], _px[2], 1)
			if color == True:
				_a = asciify.asciify(_px[0], _px[1], _px[2], 1)

			output = output + _a
		output = output + "\n"
	return output

def onePixel(r, g, b):
	return asciify.asciify(r,g,b, 1)

def color(code, rawChar):
	ansi = colorize.wrapAnsi256(code, 0)
	reset = '\x1b[0m'
	return ansi + rawChar + reset
  
class Data:
  def save(file, data):
    trueFile = open(file)
    file.write(data)

  def load(file, data):
    trueFile = open(file)
    trueFile.readline(100)

class Console:
  def clear(isServer=True):
    os.system("clear")

  def commandPrompt(key, function):
    main = input(">")
    if main == key:
      function()

  def Commentary(text):
    print(colorama.Style.DIM+ text + colorama.Style.NORMAL)
    
  def Warn(text):
    print(colorama.Fore.RED + text + colorama.Fore.RESET)

class Misc:
  def Wait(interval):
    time.sleep(interval)

  def Help():
    print("Randfunc is a python module made to make life easier and consists of many commands.\n\n\n")


class BaseClient(APIClient):
    _joke_types = ("dev", "spooky", "pun", "any")
    _image_types = (
        "aww",
        "duck",
        "dog",
        "cat",
        "memes",
        "dankmemes",
        "holup",
        "art",
        "harrypottermemes",
        "facepalm",
    )

    def _pre_init(self):
        # Convert to json before returning
        self._post_processors.append(lambda res: res.json())

    @endpoint
    def joke(self, _type: str = "any") -> dict:
        """Gets a random joke
        
        Parameters:
            - _type (str): The type of joke. Leave it or use `any` for a random type.
                           Can be: ('dev', 'spooky', 'pun', 'any')
        
        Returns:
            - str: The random joke
        """
        
        _type = _type.lower()
        if _type.lower() not in self._joke_types:
            raise RuntimeError("Unknown joke type provided: {}".format(_type))

        return Get("/joke/" + _type)

    @endpoint
    def image(self, _type: str = "aww") -> str:
        """Gets a random image
        
        Parameters:
            - _type (str): The type of joke. Use `any` for a random type.
                           Can be: ('aww', 'duck', 'dog', 'cat', 'memes', 'dankmemes', 'holup', 'art', 'harrypottermemes', 'facepalm', 'any')
        
        Returns:
            - str: The random joke
        """
        _type = _type.lower()
        if _type not in self._image_types:
            raise RuntimeError("Unknown image type provided: {}".format(_type))

        return Get("/image/" + _type)

    def close(self):
        session = self.session
        return (
            session.close() if isinstance(session, httpx.Client) else session.aclose()  # type: ignore
        )


class RandFuncV2(BaseClient):
    """
    A Wrapper for the Random Stuff API.
    Example Usage:
        rs = RandFunc(api_key = "Your API Key")
        joke = rs.joke()
        print(joke)
        rs.close()
    Example async usage:
        rs = RandFunc(async_mode=True, api_key="Your API Key")
        joke = await rs.joke()
        print(joke)
        await rs.close()
    """

    def __init__(self, *, async_mode=False, api_key: str = None):
        Session = httpx.AsyncClient if async_mode else httpx.Client
        self.base_url = "https://api.pgamerx.com"
        params = {}
        if api_key:
            params["api_key"] = api_key
        else:
            self.base_url += "/demo"

        session = Session(params=params)

        self.api_key = api_key
        super().__init__(session=session)

    @endpoint
    def ai_reply(self, msg: str, *, lang="en") -> str:
        """Gets random AI response
        
        Parameters:
            - msg (str): The message on which the response is required.
            - lang (str): The language in which response is required. It is `en` (English) by default.
        
        Returns:
            - str : The random response.
        """
        return Get("/ai/response", params={"message": msg, "language": lang})

    def _post_image(self, res):
        return res[0]

    _post_ai_reply = _post_image

class ApiPlan(Enum):
    PRO = "pro"
    ULTRA = "ultra"
    BIZ = "biz"
    MEGA = "mega"


class RandFuncV3(BaseClient):
    def __init__(
        self,
        api_key: str,
        *,
        async_mode=False,
        plan: ApiPlan = None,
        dev_name: str = None,
        bot_name: str = None,
        ai_language: str = None,
    ):
        Session = httpx.AsyncClient if async_mode else httpx.Client

        # URL construction
        self.base_url = "https://api.pgamerx.com/v3"
        if plan:
            self.base_url += "/" + plan.value

        # Authorization
        headers = {}
        if api_key:
            headers["x-api-key"] = api_key

        session = Session(headers=headers)
        self.dev_name = dev_name
        self.bot_name = bot_name
        self.ai_language = ai_language

        self.api_key = api_key
        super().__init__(session=session)

    @endpoint
    def ai_reply(
        self,
        message: str,
        *,
        unique_id: str = None,
        dev_name: str = None,
        bot_name: str = None,
        language: str = None,
    ):
        params: Dict[str, Optional[str]] = {"message": message}
        if unique_id:
            params["unique_id"] = unique_id

        if dev_name or self.dev_name:
            params["dev_name"] = dev_name or self.dev_name

        if language or self.ai_language:
            params["language"] = dev_name or self.ai_language

        if bot_name or self.bot_name:
            params["bot_name"] = bot_name or self.bot_name

        return Get("/ai/response", params=params)


class RandFuncV4(BaseClient):
    def __init__(
        self,
        api_key: str,
        *,
        async_mode=False,
        plan: ApiPlan = None,
        server: str = None,
        dev_name: str = None,
        bot_name: str = None,
        ai_language: str = None,
    ):
        Session = httpx.AsyncClient if async_mode else httpx.Client

        # URL construction
        self.base_url = "https://api.pgamerx.com/v4"
        self.plan = plan

        # Authorization
        headers = {}
        params = {}
        if api_key:
            headers["x-api-key"] = api_key
        if plan:
            params["plan"] = plan.value
        if server:
            params["server"] = server

        session = Session(headers=headers, params=params)
        self.dev_name = dev_name
        self.bot_name = bot_name
        self.ai_language = ai_language

        self.api_key = api_key
        super().__init__(session=session)

    @endpoint
    def joke(self, _type: str = "any") -> dict:
        _type = _type.lower()
        if _type.lower() not in self._joke_types:
            raise RuntimeError("Unknown joke type provided: {}".format(_type))

        return Get("/joke/", params={"type": _type})

    @endpoint
    def image(self, _type: str = "aww") -> str:
        _type = _type.lower()
        if _type not in self._image_types:
            raise RuntimeError("Unknown image type provided: {}".format(_type))

        return Get("/image/", params={"type": _type})

    @endpoint
    def ai_reply(
        self,
        message: str,
        *,
        unique_id: str = None,
        dev_name: str = None,
        bot_name: str = None,
        language: str = None,
    ):
        params: Dict[str, Optional[str]] = {"message": message}
        if unique_id:
            params["uid"] = unique_id

        if dev_name or self.dev_name:
            params["master"] = dev_name or self.dev_name

        if language or self.ai_language:
            params["language"] = dev_name or self.ai_language or "english"

        if bot_name or self.bot_name:
            params["bot"] = bot_name or self.bot_name

        if self.plan:
            url = f"/{self.plan.value}/ai/"
        else:
            url = "/ai/"
        return Get(url, params=params)


# Default alias
RandFunc = RandFuncV4

attempts_list = []
def show_score():
    if len(attempts_list) <= 0:
        print("There is currently no high score, it's yours for the taking!")
    else:
        print("The current high score is {} attempts".format(min(attempts_list)))
def number_game():
    random_number = int(random.randint(1, 10))
    print("Hello traveler! Welcome to the game of guesses!")
    player_name = input("What is your name? ")
    wanna_play = input("Hi, {}, would you like to play the guessing game? (Enter Yes/No) ".format(player_name))
    attempts = 0
    show_score()
    while wanna_play.lower() == "yes":
        try:
            guess = input("Pick a number between 1 and 10 ")
            if int(guess) < 1 or int(guess) > 10:
                raise ValueError("Please guess a number within the given range")
            if int(guess) == random_number:
                print("Nice! You got it!")
                attempts += 1
                attempts_list.append(attempts)
                print("It took you {} attempts".format(attempts))
                play_again = input("Would you like to play again? (Enter Yes/No) ")
                attempts = 0
                show_score()
                random_number = int(random.randint(1, 10))
                if play_again.lower() == "no":
                    print("That's cool, have a good one!")
                    break
            elif int(guess) > random_number:
                print("It's lower")
                attempts += 1
            elif int(guess) < random_number:
                print("It's higher")
                attempts += 1
        except ValueError as err:
            print("Oh no!, that is not a valid value. Try again...")
            print("({})".format(err))
    else:
        print("That's cool, have a good one!")

def hello():
    print("hi")

def prascii(str):
  tprint(str)

def string(length, chars='', uppercase=True, lowercase=True, digits=True):
    if chars == '':
        chars += st.ascii_uppercase if uppercase else ''
        chars += st.ascii_lowercase if lowercase else ''
        chars += st.digits if digits else ''

    return ''.join(random.choice(chars) for _ in range(length))


def integer(minimum, maximum, even=None):
    if minimum > maximum:
        raise ValueError('Minimum must not be bigger than maximum')

    def check_value(val):
        if even is True:
            if (val % 2) != 0:
                return False

        if even is False:
            if not (val & 0x1):
                return False
        return True

    while True:
        value = random.randint(minimum, maximum)
        if check_value(value):
            return value


def array(source, selection_size=1, duplicates=True):
    if not duplicates and len(source) < selection_size:
        raise ValueError('unable to select ' + str(selection_size) + ' elements from a list of size ' + str(len(source)))

    selected_elements = []
    for i in range(selection_size):
        selected_element = random.choice(source)
        selected_elements.append(selected_element)
        if not duplicates:
            source.remove(selected_element)

    return selected_elements


def datetime(start=dt.datetime(year=1970, month=1, day=1), end=dt.datetime(year=2050, month=1, day=1)):
    delta = end - start
    delta_microseconds = (delta.days * 86400000000) + (delta.seconds * 1000000) + delta.microseconds

    microseconds = integer(0, delta_microseconds)
    return start + dt.timedelta(microseconds=microseconds)


def mail(length_local=7, length_domain=5, domain_ending='com'):
    if length_local > 64:
        raise ValueError('local part must not be longer than 64 characters')

    if (length_local + length_domain + len(domain_ending)) > 254:
        raise ValueError('mail address must not be longer than 254 characters')

    return string(length_local) + '@' + string(length_domain) + '.' + domain_ending


def mac_address(prefix=None):
    mac = prefix.split(':') if prefix else list()
    while len(mac) < 6:
        mac.append('{:02x}'.format(integer(0, 255)))
    return ':'.join(mac)


def ipv4address():
    return '.'.join([str(integer(0, 255)) for _ in range(4)])


def ipv6address():
    return ':'.join('{:04x}'.format(integer(0, 65535)) for _ in range(8))



