#!/usr/bin/env python

import inputs


class XboxController:
    """ Xbox One Controller interface """

    # def __init__(self):
    max_analog = 32768
    max_trigger = 1023
    deadzone = 0.3 * max_analog
    prev = {
        "NIL": 0  # useless event
    }

    # format options
    ndigits = 3

    def check_events(self, callback=False, **kwargs):
        """ Check for new events
        if a new event is found handle method will be executed
        """
        events = inputs.get_gamepad()
        for event in events:
            # convert xbox controller event to something more usable
            resp = self.translate(event, **kwargs)

            # prevent and repetitive outputs
            if self.prev.get(resp.code) == resp.state:
                continue
            self.prev[resp.code] = resp.state

            if callable(callback):
                callback(resp)

    def response(self, event, code, state_fn):
        event.code = code
        event.state = round(state_fn(event.state), self.ndigits)

        return event

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

    def translate(self, event, **kwargs):
        # ABS_X, ABS_Y (analog), ABS_RX, ABS_RY (analog)
        # ABS_Z, ABS_RZ (trigger)
        # BTN_TL, BTN_TR (Top buttons)
        # ABS_HAT0X, ABS_HAT0Y (directional)
        # BTN_NORTH (X), BTN_SOUTH (A), BTN_EAST (B), BTN_WEST (Y)
        # SYN_REPORT
        #
        # TODO translate all what you need
        out = {
            "ABS_X": ("LX", self._analog),
            # ABS_Y": ("LY", self._analog),
            "ABS_Z": ("LZ", self._trigger),
            # "ABS_RX": ("RX", self._analog),
            # "ABS_RY": ("RY", self._analog),
            "ABS_RZ": ("RZ", self._trigger),
            # "BTN_NORTH": ("BX", self._button),
            # "BTN_SOUTH": ("BA", self._button),
            # "BTN_EAST": ("BB", self._button),
            # "BTN_WEST": ("BY", self._button),
            "BTN_MODE": ("BM", self._button),
            "ABS_HAT0X": ("DX", self._button),
        }.get(event.code, (event.code, self._button))
        # .get(event.code, ("NL") ... show only necessary
        # .get(event.code, (event.code, self._button))  ... show all events

        return self.response(event, *out)
