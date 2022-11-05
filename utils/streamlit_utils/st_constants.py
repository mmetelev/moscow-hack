import os

DARK_THEME = True
DEBUG_MODE = True if os.path.exists("C:/") else False
PAGE_CONFIG = dict(page_title="mos-app", page_icon=":page_facing_up:", layout="wide",
                   menu_items={
                       'Get Help': 'https://github.com/vsllabs-git/gloss2pose-demo/blob/master/valid_guide.md',
                       'About': "### Erydo"
                   })

CSV_TEMP_PATH = "/data/temp.csv"