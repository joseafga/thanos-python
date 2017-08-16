#!/usr/bin/env python

import inputs


class XboxController:
    """ Xbox One Controller interface """

    # def __init__(self):
    max_analog = 32768
    max_trigger = 1023
    deadzone = 0.3 * max_analog
    prev = {}

    def refresh_events(self, handle=False):
        """ Check for new events
        if a new event is found handle method will be executed

        handle : Function
            this run for every event
        """
        events = inputs.get_gamepad()
        for event in events:
            # skip if event is SYN_REPORT
            if event.code == "SYN_REPORT":
                continue

            resp = self.translate(event)

            # prevent repetitive outputs
            if self.prev.get(resp.code) == resp.state:
                continue
            self.prev[resp.code] = resp.state

            if callable(handle):
                handle(resp)

    def fix_deadzone(self, state):
        if -self.deadzone < state < self.deadzone:
            return 0
        else:
            # fix to start values after deadzone
            fix_max = self.max_analog - self.deadzone
            fix_rel = self.max_analog / fix_max

            if state > 0:
                return (state - self.deadzone) * fix_rel
            else:
                return (state + self.deadzone) * fix_rel

    def analog(self, state):
        # return (self.fix_deadzone(state) / self.max_analog + 1) / 2
        return self.fix_deadzone(state) / self.max_analog

    def trigger(self, state):
        return state / self.max_trigger

    def button(self, state):
        return state

    def translate(self, event, scale=1):

        class Response:
            def __init__(self, code, state):
                self.code = code
                self.state = state

        # ABS_X, ABS_Y (analog), ABS_RX, ABS_RY (analog)
        # ABS_Z, ABS_RZ (trigger)
        # BTN_TL, BTN_TR (Top buttons)
        # ABS_HAT0X, ABS_HAT0Y (directional)
        # BTN_NORTH (X), BTN_SOUTH (A), BTN_EAST (B), BTN_WEST (Y)
        resp = {
            "ABS_X": Response("JSL_X", self.analog(event.state)),
            "ABS_Y": Response("JSL_Y", self.analog(event.state)),
            "ABS_Z": Response("JSL_Z", self.trigger(event.state)),
            "ABS_RX": Response("JSR_X", self.analog(event.state)),
            "ABS_RY": Response("JSR_Y", self.analog(event.state)),
            "ABS_RZ": Response("JSR_Z", self.trigger(event.state)),
            "BTN_NORTH": Response("BTN_X", self.button(event.state)),
            "BTN_SOUTH": Response("BTN_A", self.button(event.state)),
            "BTN_EAST": Response("BTN_B", self.button(event.state)),
            "BTN_WEST": Response("BTN_Y", self.button(event.state)),
        }.get(event.code, Response(event.code, self.button(event.state)))

        resp.state *= scale

        return resp
