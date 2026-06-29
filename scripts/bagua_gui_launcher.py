"""PyInstaller GUI 入口（windowed 模式无控制台）。"""

from bagua.gui_dpi import enable_windows_dpi_awareness

enable_windows_dpi_awareness()

from bagua.gui import main

if __name__ == "__main__":
    main()