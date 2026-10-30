

# 0 - No logs
# 1 - Only errors
# 2 - Errors and notifications

class s_Logs:
    
    def __init__(self, _logLevel = 1):
        self.logLevel = _logLevel
    
    
    def error(self, _msg):
        if self.logLevel >= 1:
            print(f"[HEE] !! {_msg} !!")
    
    
    def notify(self, _msg):
        if self.logLevel >= 2:
            print(f"[HEE] - {_msg}")
    
    
    def notifyProgress(self, _msg):
        if self.logLevel >= 2:
            print(f"[HEE] - {_msg}", end='\r')
