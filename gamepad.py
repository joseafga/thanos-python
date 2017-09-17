#!/usr/bin/env python

import inputs


class XboxController:
    """ Xbox One Controller interface """

    # def __init__(self):
    max_analog = 32768
    max_trigger = 1023
    deadzone = 0.3 * max_analog
    prev = {}

    def check_events(self, callback=False, **kwargs):
        """ Check for new events
        if a new event is found handle method will be executed
        """
        events = inputs.get_gamepad()
        for event in events:
            # skip if event is SYN_REPORT
            if event.code == "SYN_REPORT":
                continue

            resp = self.translate(event, **kwargs)

            # prevent repetitive outputs
            if self.prev.get(resp.code) == resp.state:
                continue
            self.prev[resp.code] = resp.state

            if callable(callback):
                callback(resp)

    def fix_deadzone(self, state):
        """ Exclude deadzone value from state """
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

    def _analog(self, state):
        # return (self.fix_deadzone(state) / self.max_analog + 1) / 2
        return self.fix_deadzone(state) / self.max_analog

    def _trigger(self, state):
        return state / self.max_trigger

    def _button(self, state):
        return state

    def translate(self, event, scale=1, ndigits=3):

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
            "ABS_X": Response("L_X", self._analog(event.state)),
            "ABS_Y": Response("L_Y", self._analog(event.state)),
            "ABS_Z": Response("L_Z", self._trigger(event.state)),
            "ABS_RX": Response("R_X", self._analog(event.state)),
            "ABS_RY": Response("R_Y", self._analog(event.state)),
            "ABS_RZ": Response("R_Z", self._trigger(event.state)),
            "BTN_NORTH": Response("B_X", self._button(event.state)),
            "BTN_SOUTH": Response("B_A", self._button(event.state)),
            "BTN_EAST": Response("B_B", self._button(event.state)),
            "BTN_WEST": Response("B_Y", self._button(event.state)),
        }.get(event.code, Response(event.code, self._button(event.state)))
        # TODO: remove default response to not send unimplemented keys

        resp.state *= scale
        resp.state = round(resp.state, ndigits)

        return resp
