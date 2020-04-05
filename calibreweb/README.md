# calibreweb for hass.io
Originally copied from https://github.com/bestlibre/hassio-addon


## Description

This addon provide a [calibreweb](https://github.com/janeczku/calibre-web) container for hass.io, based on LinuxServer's Docker implementation (https://hub.docker.com/r/linuxserver/calibre-web/).

## Configuration

There is no configuration. Follow the [Quick start](https://github.com/janeczku/calibre-web#quick-start) from calibreweb :

- In the calibreweb initial setup webpage, specify "/share/calibre" as the calibre library
- Your calibre library should be contained under "hassio/share/calibre"
- use default admin/admin123 user passwd.

* The options in the "config" window in Home-Assistant are not enabled/working.
