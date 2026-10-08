# Third-party distribution notices — v1.0.0 candidate

The portable candidate bundles Python and application runtime modules, **not a browser executable**. Microsoft Edge Stable is an external Windows prerequisite controlled through Playwright's supported `msedge` channel; Prospector does not redistribute or install it. License copies for direct and necessary transitive packages are in `THIRD_PARTY_LICENSES/` beside this file. Prospector CLI itself is MIT-licensed; see `LICENSE`.

| Component | Version / role | License and authoritative source |
|---|---|---|
| Rich | 15.0.0; terminal presentation | MIT; https://github.com/Textualize/rich |
| Playwright Python | 1.61.0; browser automation | Apache-2.0; https://github.com/microsoft/playwright-python |
| Python runtime | 3.13.4; frozen interpreter and standard library | PSF License; `PYTHON_LICENSE.txt` |
| openpyxl | 3.1.5; XLSX | MIT/Expat; https://openpyxl.readthedocs.io/ |
| Beautiful Soup 4 | 4.15.0; HTML parsing | MIT; https://www.crummy.com/software/BeautifulSoup/ |
| PyInstaller | 6.22.3; build tool/bootloader | GPL-2.0-or-later with bootloader exception; https://pyinstaller.org/en/stable/license.html |

The package also carries license texts for shipped support modules (greenlet, pyee, soupsieve, et-xmlfile, markdown-it-py, mdurl/Pygments as applicable). Playwright's bundled Node.js driver carries its Node and component terms in `_internal/playwright/driver/LICENSE`; the driver package carries `LICENSE`, `NOTICE`, `ThirdPartyNotices.txt`, and bundled JavaScript sidecar notices under `_internal/playwright/driver/package/`. The PyInstaller bootloader exception text is copied into `THIRD_PARTY_LICENSES/`. R14 requires a final inventory of the actual generated distribution; this notice alone does not mark that gate complete.
