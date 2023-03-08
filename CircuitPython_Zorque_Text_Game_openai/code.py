# SPDX-FileCopyrightText: 2023 Jeff Epler for Adafruit Industries
# SPDX-License-Identifier: MIT
import os

import adafruit_esp32spi.adafruit_esp32spi_socket as socket
import adafruit_requests as requests
import adafruit_touchscreen
import board
import displayio
import terminalio
from adafruit_esp32spi import adafruit_esp32spi
from digitalio import DigitalInOut

# Use
# https://github.com/adafruit/Adafruit_CircuitPython_Touchscreen/blob/main/examples/touchscreen_calibrator_built_in.py
# to calibrate your touchscreen
touchscreen_calibration=((6616, 60374), (8537, 57269))


# set to True to use openapi, False for quicker testing of the rest of the game
# logic
use_openai = True

# Place the key in your settings.toml file
openai_api_key = os.getenv("OPENAI_API_KEY")

# Customize this prompt as you see fit to create a different experience
base_prompt = """
You are an AI helping the player play an endless text adventure game. You will stay in character as the GM.

The goal of the game is to save the Zorque mansion from being demolished. The
game starts outside the abandonded Zorque mansion.

As GM, never let the player die; they always survive a situation, no matter how
harrowing.
At each step:
    * Offer a short description of my surroundings (1 paragraph)
    * List the items I am carrying, if any
    * Offer me 4 terse numbered action choices (1 or 2 words each)

In any case, be relatively terse and keep word counts small.

In case the player wins (or loses) start a fresh game.
"""

clear='\033[2J'

def set_up_wifi():
    print(end=clear)
    if openai_api_key is None:
        print(
            "please set OPENAPI_API_KEY in settings.toml"
        )
        raise SystemExit

    wifi_ssid = os.getenv('WIFI_SSID')
    wifi_password = os.getenv('WIFI_PASSWORD')
    if wifi_ssid is None:
        print(
            "please set WIFI_SSID and WIFI_PASSWORD in settings.toml"
        )
        raise SystemExit

    esp_cs = DigitalInOut(board.ESP_CS)
    esp_ready = DigitalInOut(board.ESP_BUSY)
    esp_reset = DigitalInOut(board.ESP_RESET)

    spi = board.SPI()
    esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp_cs, esp_ready, esp_reset)
    requests.set_socket(socket, esp)

    while not esp.is_connected:
        print("Connecting to AP...")
        try:
            esp.connect_AP(wifi_ssid, wifi_password)
        except Exception as e: # pylint: disable=broad-except
            print("could not connect to AP, retrying: ", e)
            for ap in esp.scan_networks():
                print("%-24s RSSI: %d" % (str(ap["ssid"], "utf-8"), ap["rssi"]))
            continue
    print("Connected to WiFi")

def terminal_label(text, width_in_chars, palette, x, y):
    label = displayio.TileGrid(terminalio.FONT.bitmap, pixel_shader=palette,
        width=width_in_chars, height=1, tile_width=glyph_width,
        tile_height=glyph_height)
    label.x = x
    label.y = y
    term = terminalio.Terminal(label, terminalio.FONT)
    term.write(f"{text: ^{width_in_chars-1}}")
    return label

def terminal_palette(fg=0xffffff, bg=0):
    p = displayio.Palette(2)
    p[0] = bg
    p[1] = fg
    return p

def print_wrapped(text):
    print(text)
    maxwidth = main_text.width
    for line in text.split("\n"):
        col = 0
        sp = ''
        for word in line.split():
            newcol = col + len(sp) + len(word)
            if newcol < maxwidth:
                terminal.write(sp + word)
                col = newcol
            else:
                terminal.write('\r\n')
                terminal.write(word)
                col = len(word)
            sp = ' '
        if sp or not line:
            terminal.write('\r\n')
    board.DISPLAY.refresh()

def make_full_prompt(action):
    return session + [{"role": "user", "content": f"PLAYER: {action}"}]

def record_game_step(action, response):
    session.extend([
        {"role": "user", "content": f"PLAYER: {action}"},
        {"role": "assistant", "content": response.strip()},
    ])
    # Keep a limited number of exchanges in the prompt
    del session[1:-5]

def get_one_completion(full_prompt):
    if not use_openai:
        return f"""This is a canned response in offline mode. The player's last
choice was as follows: {full_prompt[-1]['content']}""".strip()
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            json={"model": "gpt-3.5-turbo", "messages": full_prompt},
            headers={
                "Authorization": f"Bearer {openai_api_key}",
            },
        )
    except Exception as e: # pylint: disable=broad-except
        print("requests exception", e)
        return None
    if response.status_code != 200:
        print("requests status", response.status_code)
        return None
    j = response.json()
    result = j["choices"][0]["message"]["content"]
    return result.strip()

def get_touchscreen_choice():
    # Wait for screen to be released
    while ts.touch_point:
        pass

    # Wait for screen to be pressed
    touch_count = 0
    while True:
        t = ts.touch_point
        if t is not None:
            touch_count += 1
            if touch_count > 5:
                break
        else:
            touch_count = 0

    # Depending on the quadrant of the screen, make a choice
    x, y, _ = t
    result = 1
    if x > board.DISPLAY.width / 2:
        result = result + 1
    if y > board.DISPLAY.height / 2:
        result = result + 2
    return result

def run_game_step(forced_choice=None):
    if forced_choice:
        choice = forced_choice
    else:
        choice = get_touchscreen_choice()
    print_wrapped(f"\n\nPLAYER: {choice}")
    prompt = make_full_prompt(choice)
    for _ in range(3):
        result = get_one_completion(prompt)
        if result is not None:
            break
    else:
        raise ValueError("Error getting completion from OpenAI")
    print(result)
    terminal.write(clear)
    print_wrapped(result)

    record_game_step(choice, result)

if use_openai:
    # Only set up wifi if using openai
    set_up_wifi()

# Set up the touchscreen
# These pins are used as both analog and digital! XL, XR and YU must be analog
# and digital capable. YD just need to be digital
ts = adafruit_touchscreen.Touchscreen(
    board.TOUCH_XL,
    board.TOUCH_XR,
    board.TOUCH_YD,
    board.TOUCH_YU,
    calibration=touchscreen_calibration,
    size=(board.DISPLAY.width, board.DISPLAY.height)
)

# Set up the 4 onscreen buttons & embedded terminal
main_group = displayio.Group()
main_group.x = 4
main_group.y = 4

# Determine the size of everything
glyph_width, glyph_height = terminalio.FONT.get_bounding_box()
use_height = board.DISPLAY.height - 8
use_width = board.DISPLAY.width - 8
terminal_width = use_width // glyph_width
terminal_height = use_height // glyph_height - 4

# Game text is displayed on this wdget
main_text = displayio.TileGrid(terminalio.FONT.bitmap, pixel_shader=terminal_palette(),
    width=terminal_width, height=terminal_height, tile_width=glyph_width,
    tile_height=glyph_height)
main_text.x = 4
main_text.y = 4 + glyph_height
terminal = terminalio.Terminal(main_text, terminalio.FONT)
main_group.append(main_text)

# Indicate what each quadrant of the screen does when tapped
label_width = use_width // (glyph_width * 2)
main_group.append(terminal_label('1', label_width, terminal_palette(0, 0xffff00), 0, 0))
main_group.append(terminal_label('2', label_width, terminal_palette(0, 0x00ffff),
    use_width - label_width*glyph_width, 0))
main_group.append(terminal_label('3', label_width, terminal_palette(0, 0xff00ff),
    0, use_height-2*glyph_height))
main_group.append(terminal_label('4', label_width, terminal_palette(0, 0x00ff00),
    use_width - label_width*glyph_width, use_height-2*glyph_height))

# Show our stuff on the screen
board.DISPLAY.auto_refresh = False
board.DISPLAY.root_group = main_group
board.DISPLAY.refresh()

# Track the game so far. ALways start with the base prompt.
session = [
        {"role": "system", "content": base_prompt.strip()},
]

try:
    run_game_step("New game")
    while True:
        run_game_step()
except (EOFError, KeyboardInterrupt) as e:
    raise SystemExit from e