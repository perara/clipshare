# clipshare
Clipshare is a configuration-less cross-platform clipboard synchronization software. The goal of this project is to keep things small and to "just work" without hassle, or time-consuming configurations. Clipshare does not care about security, so you should be careful if you wish to use this in a public environment.
Clipshare sends the clipboard across the network through UDP Multicast, which means that all listeners can snap up the clipboard. However, the traffic is compressed using lzma, so that it takes a bit of effort to read the clipboard.

## Use Cases
There is no good way of sharing a clipboard across Host/VM. Clipshare solves this by continuously broadcasting the clipboard to all listening hosts. The clipboard on the listeners. This way, all clipboards are up to date (yes, race conditions can happen, but I consider the single user case). I find this to increase the experience of using a Windows Guest for gaming when clipboards are synchronized.

## Installation
```pip install git+https://github.com/perara/clipshare.git
route add -net 224.0.0.0 netmask 240.0.0.0 dev virbr0
```
