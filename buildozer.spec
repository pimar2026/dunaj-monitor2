[app]
title = Dunaj Monitor
package.name = dunajapp
package.domain = org.dunaj
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy==2.3.0,kivymd==1.2.0,urllib3,plyer
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,NOTIFICATION
android.api = 33
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
