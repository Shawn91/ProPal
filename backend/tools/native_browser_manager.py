import webbrowser


class NativeBrowserManager:
    @staticmethod
    def search(query, engine="google"):
        if engine == "google":
            webbrowser.open(f"https://www.google.com/search?q={query}")


native_browser_manager = NativeBrowserManager()
