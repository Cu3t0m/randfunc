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
import colorama
from PIL import Image

import webbrowser
import urllib.error
import urllib.request
from enum import Enum


__version__ = "0.0.5"


_COLOR_DATA = [
	[(  0,   0,   0), colorama.Fore.LIGHTBLACK_EX, '#222'],
	[(  0,   0, 255), colorama.Fore.BLUE, '#00F'],
	[(  0, 255,   0), colorama.Fore.GREEN, '#0F0'],
	[(255,   0,   0), colorama.Fore.RED, '#F00'],
	[(255, 255, 255), colorama.Fore.WHITE, '#FFF'],
	[(255,   0, 255), colorama.Fore.MAGENTA, '#F0F'],
	[(  0, 255, 255), colorama.Fore.CYAN, '#0FF'],
	[(255, 255,   0), colorama.Fore.YELLOW, '#FF0']
]

PALETTE = [ [[(v/255.0)**2.2 for v in x[0]], x[1], x[2]] for x in _COLOR_DATA ]
CHARS_BY_DENSITY = ' .`-_\':,;^=+/"|)\\<>)iv%xclrs{*}I?!][1taeo7zjLunT#JCwfy325Fp6mqSghVd4EgXPGZbYkOA&8U$@KHDBWNMR0Q'

class Modes(Enum):
	ASCII = 'ASCII'
	TERMINAL = 'TERMINAL'
	HTML = 'HTML'
	HTML_TERMINAL = 'HTML_TERMINAL'

Back = colorama.Back

_colorama_is_init = False


class AsciiArt:
	def __init__(self, image: Image.Image):
		self._image = image

	def to_terminal(self, **kwargs):
		art = from_image(self._image, **kwargs)
		to_terminal(art)

	def to_html_file(self, path: str, mode: Modes = Modes.HTML, **kwargs):
		if mode != Modes.HTML and mode != Modes.HTML_TERMINAL:
			raise ValueError('Mode must be HTML or HTML_TERMINAL')

		art = from_image(self._image, mode=mode, **kwargs)
		to_html_file(path, art, **kwargs)

	def to_file(self, path: str, **kwargs):
		art = from_image(self._image, **kwargs)
		to_file(path, art)


def quick_test() -> None:
	to_terminal(from_url('https://source.unsplash.com/800x600?landscapes')) # type: ignore


# From URL
def _from_url(url: str) -> Image.Image:
	try:
		with urllib.request.urlopen(url) as response:
			return Image.open(response)
	except urllib.error.HTTPError as e:
		raise e from None

def from_url(url: str, **kwargs) -> str:
	img = _from_url(url)
	return from_image(img, **kwargs)

def obj_from_url(url: str) -> AsciiArt:
	return AsciiArt(_from_url(url))


# From image file
def _from_image_file(img_path: str) -> Image.Image:
	return Image.open(img_path)


def from_image_file(img_path: str, **kwargs) -> str:
	img = _from_image_file(img_path)
	return from_image(img, **kwargs)


def obj_from_image_file(img_path: str) -> AsciiArt:
	return AsciiArt(_from_image_file(img_path))


# From clipboard
def _from_clipboard() -> Image.Image:
	try:
		from PIL import ImageGrab
		img = ImageGrab.grabclipboard()
	except (NotImplementedError, ImportError):
		img = from_clipboard_linux()

	if not img:
		raise OSError('The clipboard does not contain an image')

	return img


def from_clipboard_linux() -> Image.Image:
	try:
		import gi # type: ignore
		gi.require_version("Gtk", "3.0") # type: ignore
		from gi.repository import Gtk, Gdk # type: ignore
	except ModuleNotFoundError:
		print('Accessing the clipboard under Linux requires the PyGObject module')
		print('Ubuntu/Debian: sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0')
		print('Fedora: sudo dnf install python3-gobject gtk3')
		print('Arch: sudo pacman -S python-gobject gtk3')
		print('openSUSE: sudo zypper install python3-gobject python3-gobject-Gdk typelib-1_0-Gtk-3_0 libgtk-3-0')
		exit()

	clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

	try:
		buffer = clipboard.wait_for_image()
		data = buffer.get_pixels()
		w = buffer.props.width
		h = buffer.props.height
		stride = buffer.props.rowstride
	except:
		raise OSError('The clipboard does not contain an image')

	mode = 'RGB'
	img = Image.frombytes(mode, (w, h), data, 'raw', mode, stride)
	return img


def from_clipboard(**kwargs) -> str:
	img = _from_clipboard()
	return from_image(img, **kwargs)

def obj_from_clipboard() -> AsciiArt:
	return AsciiArt(_from_clipboard())


# From image
def from_image(img, columns=120, width_ratio=2.2, char=None, mode: Modes=Modes.TERMINAL, back: colorama.ansi.AnsiBack = None, debug=False, **kwargs) -> str:
	if mode not in Modes:
		raise ValueError('Unknown output mode ' + str(mode))

	img_w, img_h = img.size
	scalar = img_w*width_ratio / columns
	img_w = int(img_w*width_ratio / scalar)
	img_h = int(img_h / scalar)
	rgb_img = img.resize((img_w, img_h))
	color_palette = img.getpalette()

	grayscale_img = rgb_img.convert("L")

	chars = [char] if char else CHARS_BY_DENSITY

	if debug:
		rgb_img.save('rgb.jpg')
		grayscale_img.save('grayscale.jpg')

	lines = []
	for h in range(img_h):
		line = ''

		for w in range(img_w):
			# get brightness value
			brightness = grayscale_img.getpixel((w, h)) / 255
			pixel = rgb_img.getpixel((w, h))
			# getpixel() may return an int, instead of tuple of ints, if the
			# source img is a PNG with a transparency layer
			if isinstance(pixel, int):
				pixel = (pixel, pixel, 255) if color_palette is None else tuple(color_palette[pixel*3:pixel*3 + 3])

			srgb = [ (v/255.0)**2.2 for v in pixel ]
			char = chars[int(brightness * (len(chars) - 1))]
			line += _build_char(char, srgb, brightness, mode)

		if mode == Modes.TERMINAL and back:
			lines.append(back + line + colorama.Back.RESET)
		else:
			lines.append(line)

	if mode == Modes.TERMINAL:
		return '\n'.join(lines) + colorama.Fore.RESET
	elif mode == Modes.ASCII:
		return '\n'.join(lines)
	elif mode == Modes.HTML or mode == Modes.HTML_TERMINAL:
		return '<br />'.join(lines)


def obj_from_image(img: Image.Image) -> AsciiArt:
	return AsciiArt(img)


def to_file(path: str, art: str) -> None:
	with open(path, 'w') as f:
		f.write(art)


def init_terminal() -> None:
	global _colorama_is_init
	if not _colorama_is_init:
		colorama.init()
		_colorama_is_init = True


def to_terminal(ascii_art: str) -> None:
	init_terminal()
	print(ascii_art)


def to_html_file(
	path: str,
	art: str,
	styles: str = 'display: inline-block; border-width: 4px 6px; border-color: black; border-style: solid; background-color:black; font-size: 8px;',
	additional_styles: str= '',
	auto_open: bool = False,
	**kwargs,
) -> None:
	html = f"""<!DOCTYPE html>
<head>
	<title>ASCII art</title>
	<meta name="generator" content="ASCII Magic {__VERSION__} - https://github.com/Cu3t0m/randfunc/" />
</head>
<body>
	<pre style="{styles} {additional_styles}">{art}</pre>
</body>
</html>"""
	with open(path, 'w') as f:
		f.write(html)
	if auto_open:
		webbrowser.open(path)


def _convert_color(rgb: list, brightness: float) -> dict:
	min_distance = 2
	index = 0

	for i in range(len(PALETTE)):
		tmp = [ v*brightness for v in PALETTE[i][0] ]
		distance = _L2_min(tmp, rgb)

		if distance < min_distance:
			index = i
			min_distance = distance

	return {
		'term': PALETTE[index][1],
		'hex-term': PALETTE[index][2],
		'hex': '#{:02x}{:02x}{:02x}'.format(*(int(c*200+55) for c in rgb)),
	}


def _L2_min(v1: list, v2: list) -> float:
    return (v1[0]-v2[0])**2 + (v1[1]-v2[1])**2 + (v1[2]-v2[2])**2


def _build_char(char: str, srgb: list, brightness: float, mode: Modes = Modes.TERMINAL) -> str:
	color = _convert_color(srgb, brightness)

	if mode == Modes.TERMINAL:
		return color['term'] + char
	
	elif mode == Modes.ASCII:
		return char

	elif mode == Modes.HTML_TERMINAL:
		c = color['hex-term']
		return f'<span style="color: {c}">{char}</span>'

	elif mode == Modes.HTML:
		c = color['hex']
		return f'<span style="color: {c}">{char}</span>'

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



