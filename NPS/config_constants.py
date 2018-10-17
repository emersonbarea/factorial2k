### FILE PATHS

## GENERAL PATHS
PYTHONPATH = '/usr/bin/python'
NPS_PATH = '/home/mininet/nps/'
CONTROLLER_PATH = '/home/mininet/floodlight-0.90/'
GUI_HTML = $NPS_PATH + 'GUI/GUI.html'

## SCRIPT PATHS
SRC_SCRIPT_FOLDER = $NPS_PATH + '/scripts/'
DST_SCRIPT_FOLDER = $NPS_PATH + '/clusternode/MininetScripts/'

## CONFIG PATHS
NODELIST_FILEPATH = $NPS_PATH + '/config/nodelist.txt'
MAIN_DB_PATH      = $NPS_PATH + '/tmp/'

NPS_CONTROL_NODE_IP = '192.168.254.1'

### MALWARE MODE
MALWARE_MODE_ON = False

### HOSTS CONFIG
FIRST_HOST_IP = '1.2.3.1'
HOST_NETMASK = 16
LINK_DELAY = 5
NO_DELAY_FLAG = True

### CLUSTER NODE CONFIG
CLUSTER_NODE_MACHINE_NAME = 'node1'

### MININETCE SIMULATION MODES CONSTANTS
CLI_MODE = True

### APPIRANCE CONFIG
STRING_ALIGNMENT = 45
ALPHA_VALUE = 0.33
CLI_PROMPT_STRING = ''
VIEW_PROGRAMM_NAME = 'Preview'
RESULT_PIC_DPI = 300

### GENERAL CONFIG
DRAWING_FLAG = False
DRAWING_POS_FLAG = False
SCRIPT_FOLDER = SRC_SCRIPT_FOLDER + '/nodes/'
CHECK_PING_TIME_PERIOD = 30

### CONTROLLER CONFIG
REMOTE_CONTROLLER_IP   = $NPS_CONTROL_NODE_IP
REMOTE_CONTROLLER_PORT = '6633'

### WEB SOCKET SERVER CONFIG
WEB_SOCKET_SERVER_IP   = $NPS_CONTROL_NODE_IP
WEB_SOCKET_SERVER_PORT = '9876'

### MSGEXCH SERVER CONFIG
MSGEXCH_SERVER_PATH = $NPS_PATH + '/src'
MSGEXCH_SERVER_IP   = $NPS_CONTROL_NODE_IP
MSGEXCH_SERVER_PORT = '9877'