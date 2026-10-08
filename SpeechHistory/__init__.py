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
from collections import deque

class SpeechHistory(Extension):
	# Provides a history of Orca's speech
	# Metadata
	GROUP_LABEL="Speech History"
	DESCRIPTION = "History of speech announcements"
	VERSION="2.0"
	AUTHOR="José Pérez"

	# Constructor
	def __init__(self) -> None:
		super().__init__()
		self._history: deque[str] = deque(maxlen=500)
		self._history_pos: int = 0
		# Flag to prevent recursion
		self._stop_history_append: bool = False
		self._recording: bool = False
		self._recorded: list[str] = []

	# Speech hook
	def on_speech_output(self, output: SpeechOutput) -> SpeechOutputResult | None:
		if self._stop_history_append:
			return None

		text = output.text
		if text and text.strip():
			self._history.appendleft(text)
			self._history_pos = 0
			if self._recording:
				self._recorded.append(text)
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

			# Start recording
			KeyboardCommand(
				"startRecording",
				self._start_recording,
				self.GROUP_LABEL,
				"Start recording speech output",
				desktop_keybinding=keybindings.KeyBinding(
					"F11",
					keybindings.ORCA_SHIFT_MODIFIER_MASK,
				),
				laptop_keybinding=keybindings.KeyBinding(
					"F11",
					keybindings.ORCA_SHIFT_MODIFIER_MASK,
				),
			),

			# Stop recording
			KeyboardCommand(
				"stopRecording",
				self._stop_recording,
				self.GROUP_LABEL,
				"Stop recording speech output and copy it to the clipboard",
				desktop_keybinding=keybindings.KeyBinding(
					"F12",
					keybindings.ORCA_SHIFT_MODIFIER_MASK,
				),
				laptop_keybinding=keybindings.KeyBinding(
					"F12",
					keybindings.ORCA_SHIFT_MODIFIER_MASK,
				),
			),
		]

	def _copy_last(self) -> bool:
		if not self._history:
			self.controller.present_message_internal("There are no items in history")
			return True

		# Get the text at the current position and copy it to the clipboard
		text = self._history[self._history_pos]
		self.controller.set_clipboard_text_internal(text)
		self.controller.play_tone_internal(0.12, 1000, volume=0.5)
		return True

	def _prev_string(self) -> bool:
		if not self._history:
			self.controller.present_message_internal("There are no items in history")
			return True

		self._history_pos += 1

		# Check upper limit
		if self._history_pos > len(self._history) - 1:
			self._history_pos -= 1
			self.controller.play_tone_internal(0.12, 500, volume=0.5)

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
			self.controller.play_tone_internal(0.12, 500, volume=0.5)

		text = self._history[self._history_pos]
		self._stop_history_append = True
		self.controller.present_message_internal(text)
		self._stop_history_append = False
		return True

	def _start_recording(self) -> bool:
		if self._recording:
			self._stop_history_append = True
			self.controller.present_message_internal("Already recording speech")
			self._stop_history_append = False
			return True

		self._recording = True
		self._stop_history_append = True
		self.controller.present_message_internal("Started recording speech")
		self._stop_history_append = False
		return True

	def _stop_recording(self) -> bool:
		if not self._recording:
			self._stop_history_append = True
			self.controller.present_message_internal("Not currently recording speech")
			self._stop_history_append = False
			return True

		self._recording = False
		self.controller.set_clipboard_text_internal("\n".join(self._recorded))
		self._recorded.clear()
		self._stop_history_append = True
		self.controller.present_message_internal("Recorded speech copied to clipboard")
		self._stop_history_append = False
		return True
