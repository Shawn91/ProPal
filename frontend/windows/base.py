from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QWidget

from backend.agents.llm_agent import LLMResult
from backend.tools.utils import logger


class FramelessWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setMouseTracking(True)
        self.mouse_pos = None

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            # Capture the current mouse position
            self.mouse_pos = event.globalPos() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.LeftButton:
            # Calculate the new position of the window
            new_pos = event.globalPos() - self.mouse_pos
            self.move(new_pos)
            event.accept()


class LLMRequestThread(QThread):
    content_received = Signal(str)
    result_received = Signal(LLMResult)

    def __init__(self, llm_agent, user_input: str = ""):
        super().__init__()
        self.llm_agent = llm_agent
        self.user_input = user_input
        self.stop_flag = False  # whether to stop the thread

    def run(self):
        response = self.llm_agent.act(trigger_attrs={"user_input": self.user_input})
        while True:
            if self.stop_flag:
                llm_result = response.send("STOP")  # stop streaming response
                self.result_received.emit(llm_result)
                self.reset()
                break

            try:
                chunk = next(response)
                if isinstance(chunk, str):
                    self.content_received.emit(chunk)
                elif isinstance(chunk, LLMResult):
                    self.result_received.emit(chunk)
            except StopIteration:
                self.reset()
                break
            except Exception as e:
                logger.error(f"error when receiving response from llm agent: {e}")
                raise e

    def reset(self):
        """restore the thread to initial state"""
        self.stop_flag = False
        self.user_input = ""
