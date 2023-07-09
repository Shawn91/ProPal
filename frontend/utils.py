import re
from urllib import request
from urllib.error import URLError

from PySide6.QtCore import QThread, Signal

from frontend import version


class NewVersionChecker(QThread):
    NEW_VERSION_AVAILABLE = Signal(str)
    VERSION_PAT = re.compile(r'v\d{1,2}\.\d{1,2}\.\d{1,2}')

    def get_latest_published_version(self) -> str:
        url = 'https://github.com/Shawn91/ProPal/releases'
        try:
            response = request.urlopen(url, timeout=10)
        except URLError:
            return ''
        html = response.read().decode()
        version = self.VERSION_PAT.search(html)
        if version:
            return version.group(0)[1:]
        return ''

    @staticmethod
    def check_new_version_available(remote_version: str, local_version: str = version) -> bool:
        try:
            remote_version_semantics = [int(i) for i in remote_version.split('.')]
            local_version_semantics = [int(i) for i in local_version.split('.')]
            for idx in range(2):
                if remote_version_semantics[idx] > local_version_semantics[idx]:
                    return True
                elif remote_version_semantics[idx] < local_version_semantics[idx]:
                    return False
                else:
                    continue
            return False
        except:
            return False

    def run(self):
        remote_version = self.get_latest_published_version()
        if not remote_version:
            return
        if self.check_new_version_available(remote_version=remote_version, local_version=version):
            self.NEW_VERSION_AVAILABLE.emit(remote_version)
