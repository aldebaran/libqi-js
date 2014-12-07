#! /usr/bin/python

import qi
import sys

class JSTest:

    def __init__(self):
        self.signal = qi.Signal()
        self.property = qi.Property()
        self.property.setValue(42)

    def constant_string(self):
        return "lol"

    def constant_void(self):
        return

    def echo_value(self, value):
        return value

def main():
    app = qi.ApplicationSession(sys.argv)
    app.start()
    session = app.session
    jst = JSTest()
    session.registerService("JSTest", jst)
    app.run()

if __name__ == "__main__":
    main()
