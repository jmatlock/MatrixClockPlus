"""
Matrix Clock Plus
by James Matlock
Jan 2021

This project is a mashup and extension of example projects for the
Adafruit Matrix Portal. In order to run this project you will need the
following hardware:

- Adafruit Matrix Portal (https://www.adafruit.com/product/4745)
- 64 x 32 RGB LED Matrix (https://www.adafruit.com/product/2277)
- 5V USB C Power Supply (https://www.adafruit.com/product/4298)

This project assumes CircuitPython is already installed on the Matrix Portal.
More information about installing CircuitPython can be found here:
    https://learn.adafruit.com/adafruit-matrixportal-m4/install-circuitpython

This project will also require CircuitPython libraries to be included in a
lib folder when the project is installed on the CIRCUITPY drive of
the Matrix Portal:
    adafruit_bitmap_font
    adafruit_bus_device
    adafruit_display_text
    adafruit_esp32spi
    adafruit_io
    adafruit_lis3dh.mpy
    adafruit_matrixportal
    adafruit_requests.mpy
    neopixel.mpy

See this page for more info about installing CircuitPython libraries:
    https://learn.adafruit.com/welcome-to-circuitpython/circuitpython-libraries

This project is under development.

Currently the clock has the following features:
- Tells time
- Shows date and day of the week
- Shows the temperature from openweathermap.org

The plan is for the clock to have the following features:
- Display "days/weeks/months" until event information.
- Collect weather info from openweathermap.org and display.
- Use fixed and scrolling text display. Possibly develop a vertical scrolling
  method for added variety.
- Scrape news information and display.
- Allow configuration via MQTT client/broker.
- Add interesting "screen saver" or transition options with wipes, game of life,
  fractal, or other animations.

Tutorials and references used as input to this project include:
- https://learn.adafruit.com/network-connected-metro-rgb-matrix-clock
- https://learn.adafruit.com/weather-display-matrix
- https://learn.adafruit.com/creating-projects-with-the-circuitpython-matrixportal-library
"""

import time
import board
import displayio
import terminalio
from adafruit_display_text.label import Label
from adafruit_bitmap_font import bitmap_font
from adafruit_matrixportal.network import Network
from adafruit_matrixportal.matrix import Matrix

BLINK = True
DEBUG = False

months = ['na', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
wkdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise
print("    Matrix Clock Plus")
print("Time will be set for {}".format(secrets["timezone"]))

# --- Display setup ---
matrix = Matrix()
display = matrix.display
network = Network(status_neopixel=board.NEOPIXEL, debug=False)

# --- Weather data setup ---
UNITS = "imperial"
DATA_LOCATION = []
DATA_SOURCE = (
        "http://api.openweathermap.org/data/2.5/weather?q=" + secrets["openweather_loc"] + "&units=" + UNITS
)
DATA_SOURCE += "&appid=" + secrets["openweather_token"]
current_temp = '0'

# --- Drawing setup ---
group = displayio.Group(max_size=4)  # Create a Group
bitmap = displayio.Bitmap(64, 32, 2)  # Create a bitmap object,width, height, bit depth
color = displayio.Palette(4)  # Create a color palette
color[0] = 0x000000  # black background
color[1] = 0xFF0000  # red
color[2] = 0xCC4000  # amber
color[3] = 0x85FF00  # greenish

# Create a TileGrid using the Bitmap and Palette
tile_grid = displayio.TileGrid(bitmap, pixel_shader=color)
group.append(tile_grid)  # Add the TileGrid to the Group
display.show(group)

if not DEBUG:
    # font = bitmap_font.load_font("fonts/IBMPlexMono-Medium-24_jep.bdf")
    font = bitmap_font.load_font("fonts/Arial-14.bdf")
    font2 = bitmap_font.load_font("fonts/Arial-12.bdf")
else:
    font = terminalio.FONT
    font2 = terminalio.FONT

clock_label = Label(font, max_glyphs=6)
test_label = Label(font2, max_glyphs=32)

DATA_LOCATION = []


class Weather:
    weather_refresh = None
    weather_data = None


class Events:
    def __init__(self):
        self.index = 0
        self.events = {'Christmas': [12, 25],
                  'Halloween': [10, 31],
                  'My birthday': [5, 29],
                  'July 4': [7, 4],
                  }

    def get_next_event_string(self):
        event = list(self.events.items())[self.index]
        self.index += 1
        if self.index >= len(self.events):
            self.index = 0
        return f'{event[0]} occurs on {event[1][0]}/{event[1][1]}'

def get_weather_info():
    try:
        value = network.fetch_data(DATA_SOURCE, json_path=(DATA_LOCATION,))
        print("Response is", value)
        return value
    except RuntimeError as e:
        print("Some error occurred, retrying! -", e)
        return None


def update_time(*, hours=None, minutes=None, show_colon=False,
                weather=None):
    now = time.localtime()  # Get the time values we need
    # Update weather data every 10 minutes
    if (not weather.weather_refresh) or (time.monotonic() - weather.weather_refresh) > 600:
        weather.weather_data = get_weather_info()
        if weather.weather_data:
            weather.weather_refresh = time.monotonic()

    # print(now)
    if hours is None:
        hours = now[3]
    if hours >= 18 or hours < 6:  # evening hours to morning
        clock_label.color = color[1]
    else:
        clock_label.color = color[3]  # daylight hours
    if hours > 12:  # Handle times later than 12:59
        hours -= 12
    elif not hours:  # Handle times between 0:00 and 0:59
        hours = 12

    if minutes is None:
        minutes = now[4]

    if BLINK:
        colon = ":" if show_colon or now[5] % 2 else " "
    else:
        colon = ":"

    if now[5] % 20 < 10:
        clock_label.text = "{hours}{colon}{minutes:02d}".format(
            hours=hours, minutes=minutes, colon=colon
        )
        clock_label.font = font
    elif now[5] % 20 < 13:
        clock_label.text = f"{wkdays[now[6]]}"
    elif now[5] % 20 < 16:
        clock_label.text = f"{months[now[1]]} {now[2]}"
    else:
        try:
            temperature = int(weather.weather_data["main"]["temp"])
        except Exception as e:
            temperature = "??"
        clock_label.text = f"{temperature}°F"

    bbx, bby, bbwidth, bbh = clock_label.bounding_box
    # Center the label
    clock_label.x = round(display.width / 2 - bbwidth / 2)
    clock_label.y = display.height // 4
    if DEBUG:
        print("Label bounding box: {},{},{},{}".format(bbx, bby, bbwidth, bbh))
        print("Label x: {} y: {}".format(clock_label.x, clock_label.y))


def update_second_line(value):
    test_label.text = f'{value}'
    bbx, bby, bbwidth, bbh = test_label.bounding_box
    x = round(display.width / 2 - bbwidth / 2)
    if x < 0:
        test_label.x = 0
    else:
        test_label.x = x
    test_label.y = display.height // 4 * 3


weather = Weather()
events = Events()
last_check = None
update_time(show_colon=True, weather=weather)  # Display whatever time is on the board
update_second_line('?')
group.append(clock_label)  # add the clock label to the group
group.append(test_label)

counter = 0
while True:
    counter += 1
    if last_check is None or time.monotonic() > last_check + 3600:
        try:
            update_time(
                show_colon=True,
                weather=weather
            )  # Make sure a colon is displayed while updating
            network.get_local_time()  # Synchronize Board's clock to Internet
            last_check = time.monotonic()
        except RuntimeError as e:
            print("Some error occured, retrying! -", e)

    update_time(weather=weather)
    if counter % 4 == 0:
        event_txt = events.get_next_event_string()
        update_second_line(event_txt)
        if counter >= 100:
            counter = 0
        print(event_txt)

    time.sleep(1)
