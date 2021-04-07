import sys
import transforms

from maltego_trx.registry import register_transform_function, register_transform_classes
from maltego_trx.server import app, application
from maltego_trx.handler import handle_run

import maltego_trx.maltego
# hotfix until adjusted in upstream
maltego_trx.maltego.DISP_INFO_TEMPLATE = "<Label Name=\"%(name)s\" Type=\"text/html\"><![CDATA[%(content)s]]></Label>"

register_transform_classes(transforms)

handle_run(__name__, sys.argv, app)
