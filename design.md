# Linux Control Skill Design:
---
| user say: | mycroft does: |
|-----------|---------------|
| "increase the volume" | increases volume |
|"lock the computer"|locks the computer|
|"open `program`"|launches program "here" where ever that is|
|"open `program` on `desktop`"|opens program on desktop|
|"launch configuration `layout`"|looks though its data base to find a lay out file called `layout` and sets things up like that in an idempotent way (it it doesn't need to do something, don't)|
|"set up `layout`"|see above ^|
|"switch to `desktop`"|switches to `desktop`|
|move to `desktop`|move the current window (node in bspwm speak) to `desktop`|
|raise the screen brightness|raises the screen brightness by a default amount.|
|raise the screen brightness by `percent`|raises the screen brightness by `percent`|
|set volume max|set volume to 100 percent|
|set brightness max|sets the screen backlight to max|
|||
