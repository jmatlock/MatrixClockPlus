Matrix Portal Clock Plus

**This project is part of a #100DaysOfCode challenge!**

This CircuitPython project will drive an RGB LED Matrix using an Adafruit
Matrix Portal to show the time, weather, and other interesting information.
Much of this project is a mashup of many of the tutorials provided by Adafruit,
but there will be a some original ideas in here as well to make this a 
useful, configurable clock.

Initially this display will just combine a clock with weather information,
"days until" information about events, and possibly other scraped web
information. In more advanced versions of this project, I hope to use a
local MQTT server as a means for configuring the clock while it is running
without needing to update the code.

### To be done for MVP version 1:
- [x] Display the time and date.
- [x] Display the current weather (from openweathermap.org).
- [x] Display "days until" events that have been configured on the device.
- [x] Use Up/Down buttons to change text colors.

### To be done for advanced versions:
- [ ] Display the weather forecast.
- [ ] Show news headlines from scraped news sites.
- [ ] Provide an alarm function (configuration means TBD)
- [ ] Setup an MQTT Server to be used for passing configuration or data
feed information.
- [ ] Enable the Matrix Portal to be an MQTT Client which can subscribe
to the configuration server for updates.
- [ ] Enable events via IFTTT, Alexa, and Node-Red to support scenarios
like using voice to request something to be displayed.