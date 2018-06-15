## Preparing Raspbian for g_ether

This allows the Raspberry Pi Zero's USB OTG (On The Go) port to serve as an ethernet connection.

### Update config.txt

- Open config.txt for editing
  ```sudo vim /boot/config.txt```
- Add the following to the bottom of the file, on a its own line:
  ```dtoverlay=dwc2```
- Save

### Update cmdline.txt

- Open cmdline.txt for editing
  ```sudo vim /boot/cmdline.txt```
- Add a space and the following after `rootwait`:
  ```modules-load=dwc2,g_ether```
- Save


### Update usb0 interface

If you would like to share your Mac's internet connection with the Pi Zero, then make the following changes to the Pi's interfaces file:

- Open interfaces
  ``sudo vim /etc/network/interfaces
- Change `auto lo` to `auto lo usb0`
- Add the following at the end of the file:
```
allow hotplug usb0
iface usb0 inet manual
```


### VNC

- start manually: ```sudo systemctl start vncserver-x11-serviced.service```
- start automatically: ```sudo systemctl enable vncserver-x11-serviced.service```
