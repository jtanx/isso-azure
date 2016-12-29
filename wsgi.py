#!/usr/bin/env python
import site, os

from isso import make_app
from isso import config as isso_config

ISSO_CONFIG=os.path.abspath(os.path.join(".", "production.cfg"))

print("ISSO CONFIG:", ISSO_CONFIG)
application = make_app(isso_config.load(ISSO_CONFIG))