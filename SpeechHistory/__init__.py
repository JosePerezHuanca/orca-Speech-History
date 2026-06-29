# Orca Extension: Speech History
# Copyright (C) 2026 José Pérez
#
# Based on NVDA Speech History Add-on
# See: https://github.com/jscholes/nvda-speech-history
#
# This file is covered by the GNU General Public License.


from orca import keybindings
from orca.command import Command, KeyboardCommand
from orca.extension import Extension, SpeechOutput, SpeechOutputResult
from orca.sound import get_player, Tone
from orca.clipboard import get_presenter
from collections import deque

class SpeechHistory(Extension):
	# Provides a history of Orca's speech
	# Metadata
	GROUP_LABEL="Speech History"
	DESCRIPTION = "History of speech announcements"
	VERSION="1.0"
	AUTHOR="José Pérez"

	# Constructor
	def __init__(self) -> None:
		super().__init__()
		self._history: deque[str] = deque(maxlen=500)
		self._history_pos: int = 0
		self._beep_frequency = 1500  # Hz
		self._beep_duration = 120    # ms
		# Flag to prevent recursion
		self._stop_history_append: bool = False

	# Speech hook
	def on_speech_output(self, output: SpeechOutput) -> SpeechOutputResult | None:
		if self._stop_history_append:
			return None

		text = output.text
		if text and text.strip():
			self._history.appendleft(text)
			self._history_pos = 0
		return None

	# Commands
	def _get_commands(self) -> list[Command]:
		return [
			# Copy last item
			KeyboardCommand(
				"copyLast",
				self._copy_last,
				self.GROUP_LABEL,
				"Copy the current history item to the clipboard",
				desktop_keybinding=keybindings.KeyBinding(
					"F12",
					keybindings.NO_MODIFIER_MASK,
				),
				laptop_keybinding=keybindings.KeyBinding(
					"F12",
					keybindings.NO_MODIFIER_MASK,
				),
			),

			# Previous item
			KeyboardCommand(
				"prevString",
				self._prev_string,
				self.GROUP_LABEL,
				"Review previous history item",
				desktop_keybinding=keybindings.KeyBinding(
					"F11",
					keybindings.SHIFT_MODIFIER_MASK,
				),
				laptop_keybinding=keybindings.KeyBinding(
					"F11",
					keybindings.SHIFT_MODIFIER_MASK,
				),
			),

			# Next item
			KeyboardCommand(
				"nextString",
				self._next_string,
				self.GROUP_LABEL,
				"Review next history item",
				desktop_keybinding=keybindings.KeyBinding(
					"F12",
					keybindings.SHIFT_MODIFIER_MASK,
				),
				laptop_keybinding=keybindings.KeyBinding(
					"F12",
					keybindings.SHIFT_MODIFIER_MASK,
				),
			),
		]

	def _copy_last(self) -> bool:
		if not self._history:
			self.controller.present_message_internal("There are no items in history")
			return True

		# Get the text at the current position and copy it to the clipboard
		text = self._history[self._history_pos]
		clipboard = get_presenter()
		clipboard.set_text(text)
		self._beep(1000, 120)
		return True

	def _prev_string(self) -> bool:
		if not self._history:
			self.controller.present_message_internal("There are no items in history")
			return True

		self._history_pos += 1

		# Check upper limit
		if self._history_pos > len(self._history) - 1:
			self._history_pos -= 1
			self._beep(500, 120)

		text = self._history[self._history_pos]
		self._stop_history_append = True
		self.controller.present_message_internal(text)
		self._stop_history_append = False
		return True

	def _next_string(self) -> bool:
		if not self._history:
			self.controller.present_message_internal("There are no items in history")
			return True

		self._history_pos -= 1

		# Check lower limit
		if self._history_pos < 0:
			self._history_pos += 1
			self._beep(500, 120)

		text = self._history[self._history_pos]
		self._stop_history_append = True
		self.controller.present_message_internal(text)
		self._stop_history_append = False
		return True

	def _beep(self, frequency: int, duration_ms: int) -> None:
		player = get_player()
		tone = Tone(
			duration=duration_ms / 1000.0,
			frequency=frequency,
			volume=0.5
		)
		player.play(tone)
