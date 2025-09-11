import sys
from PyQt5.QtWidgets import QApplication
from ui.chat_ui import ChatUI

if __name__ == "__main__":
    app = QApplication(sys.argv)
    chat = ChatUI()
    chat.show()
    sys.exit(app.exec_())
