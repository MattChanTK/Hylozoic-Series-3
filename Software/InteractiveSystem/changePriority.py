from ctypes import windll,c_bool,c_uint
from os import getpid

GetPriorityClass    = windll.kernel32.GetPriorityClass
SetPriorityClass    = windll.kernel32.SetPriorityClass
OpenProcess         = windll.kernel32.OpenProcess
CloseHandle         = windll.kernel32.CloseHandle

class Priorities():
    ABOVE_NORMAL_PRIORITY_CLASS     = 0x8000
    BELOW_NORMAL_PRIORITY_CLASS     = 0x4000
    HIGH_PRIORITY_CLASS             = 0x0080
    IDLE_PRIORITY_CLASS             = 0x0040
    NORMAL_PRIORITY_CLASS           = 0x0020
    REALTIME_PRIORITY_CLASS         = 0x0100
    order = [0x0040,0x4000,0x0020,0x8000,0x0080,0x0100]
    reverseOrder = {'0x40':0,'0x4000':1,'0x20':2,'0x8000':3,'0x80':4,'0x100':5}

__shouldClose = [False]

def getProcessHandle( process, inherit = False ):
    __shouldClose[ 0 ] = True
    if not process:
        process = getpid()
    return OpenProcess( c_uint( 0x0200 | 0x0400 ), c_bool( inherit ), c_uint( process ) )

def SetPriorityById( priority, process = None, inherit = False ):
    return SetPriority( priority, getProcessHandle( process, inherit ) )

def SetPriority( priority, process = None, inherit = False ):
    if not process:
        process = getProcessHandle( None, inherit )
    result = SetPriorityClass( process, c_uint( priority ) ) != 0
    if __shouldClose:
        CloseHandle(process)
        __shouldClose[ 0 ] = False
    return result

def IncreasePriorityById( process = None, inherit = False, times = 1 ):
    return IncreasePriority( getProcessHandle( process, inherit, times ) )
def IncreasePriority( process = None, inherit = False, times = 1 ):
    if times <1:
        raise ValueError("Wrong value for the number of increments")
    if not process:
        process = getProcessHandle( None, inherit )
    currentPriority = Priorities.reverseOrder[ hex( GetPriorityClass (process) ) ]
    if currentPriority < ( len( Priorities.order ) - 1 ):
        return SetPriority( Priorities.order[ min( currentPriority + times, len( Priorities.order ) - 1) ], process )
    return False
def DecreasePriorityById( process = None, inherit = False, times = 1 ):
    return DecreasePriority( getProcessHandle( process, inherit, times ) )
def DecreasePriority( process = None, inherit = False, times = 1 ):
    if times <1:
        raise ValueError("Wrong value for the number of decrements")
    if not process:
        process = getProcessHandle( None, inherit )
    currentPriority = Priorities.reverseOrder[ hex( GetPriorityClass( process ) ) ]
    if currentPriority > 0:
        return SetPriority( Priorities.order[ max(0,currentPriority - times) ], process )
    return False
