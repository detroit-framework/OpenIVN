"""Views, one for each OpenIVN page."""
from openivn.views.authentication import login, logout, callback
from openivn.views.index import show_index
from openivn.views.register import register
from openivn.views.apps import view_apps
from openivn.views.downloads import view_downloads, download_trace
from openivn.views.edit_app import edit_app
from openivn.views.udp_test import test_udp, clear_udp
from openivn.views.tcp_test import test_tcp, clear_tcp
