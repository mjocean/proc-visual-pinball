#########
## register_vpcom.py
##
## a Visual Pinball to P-ROC COM Bridge
##  that provides a P-ROC-less and pinball-machine-less 
##  pyprocgame simulation and testing environment. 
##
##  All credit goes to destruk, Gerry Stellenberg and Adam Preble; all I'm 
##   doing is trying to keep it current.  The basic idea is to make this option
##   better for folks doing pyprocgame development using VP to test imperfect code.
##   logging is better now, and you should have to make fewer changes to the VBScript
##   in a VP table for this to work.
## 
##  See the GitHub page for instructions for use
##
## changes: 
##     1.29.2017: (at long last)
##          0. The dreaded R6034 runtime error dialog no longer appears
##          1. Games can be restarted without quitting visual pinball
##          2. Python code changes will be reloaded on next play without quitting/relaunching VP
##          3. Print commands will no longer kill the application (and you can see them!)
##              run C:\Python26\Lib\site-packages\win32\lib\win32traceutil.pyc 
##              that program shows the lost print statements (that don't make it to the log)!
##          4. Removed calls to deprecated method `self.game.log()` to support games that 
##              remap log for something else
##     12.28.2014:
##          0. Re-ordered and deferred imports and changed how config is loaded so that a 
##              config.yaml in the game directory will be loaded/used.  Also a procgame
##              directory in the game directory will be used, if present.
##      8.27.2014:
##          0. Fixed some bugs introduced by Sys11 support that broke non-Sys11 (e.g., WPC support).
##          1. Added in System11 ACRelay 'renumbering' (a/k/a lying) like pinmame does.  Fewer changes
##              to run stock tables.
##      8.24.2014:
##          This is the first version with "automatic" System 11 and Data East support.
##          in your VBScript for the table, also set the Controller's new Sys11 property as:
##              controller.Sys11=True
##          this will have the VPCOM bridge auto-renumber lamps and switches from the 1-64
##          numbering in the manual (and that all Sys11/DE VPT tables use) to the P-ROC expected
##          Col/Row numbering.  No more renumbering all the lamps and switches in the VBScript
##          for System11 and Data East machines.  Tested on DE Hook.
##      8.12.2014:
##          0. Fixed some bugs that were still preventing full stack traces to be logged 
##              on "initialization time" failures
##      8.03.2014:
##          0. Full stack traces will be logged on "initialization time" failures
##      5.30.2014:
##          0. Added the ability to track if the game has crashed and respond to successive COM
##              calls with a COMException so that Visual Pinball will show a dialog box on Python
##              failure, and the dialog actually tells you where in the Python the code crashed.
##          1. Fixed the formatting on the logged stack trace on failure. 
##      5.25.2014:
##          0. Switches to the directory that contains the game prior to running.  Without this
##             you might have needed a lot of changes to your game code to not use '.' in paths
##          1. Better logging throughout.  Anything in the PyProcGame side that causes 
##             the game code to crash at any point (from init to execution) will now add an
##             exception into the log file.  This makes debugging possible
##                  TIP: use the MinGW command 'tail' to monitor your log as you execute!
##                      For me this is: tail -f /c/P-ROC/shared/log.txt 
##          2. added an optional second arg to Run --apparently some tables send it and
##             I don't know why.  Ignoring it is safe.
##          3. Removed the separate init path for CCC -- epthegeek changed his code a while back
##             such that this is no longer required
##      01.03.2013:
##          1.  Added another SetMech interface/method with three args so fewer VP tables 
##          need to be editted before running
##          2.  Some hacks are in the code with very alpha support for Mechs in T2 (which are 
##          supported in the simulator files (t2.cpp) in PinMame);  Check setMech and getMech

import os
import sys
from win32com.server.exception import COMException
import winerror

# this was previously here to find procgame in c:\p-roc --now we don't want that one, yet...
# sys.path.append(sys.path[0]+'/..') 

import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", filename="/P-ROC/shared/log.txt")

import pinproc
import win32com
import pythoncom
import win32com.server.util
from win32com.server.util import wrap, unwrap
import thread
import yaml

try:
    import pygame
    import pygame.locals
except ImportError:
    print "Error importing pygame; ignoring."
    pygame = None

class ISettings:
    _public_methods_ = []
    _public_attrs_ = [  'Value']

    def Value(self, item, item2):
        return True
    def SetValue(self, item, item2):
        return True

class IGames:
    _public_methods_ = []
    _public_attrs_ = [  'Settings']

    def Settings(self):
        settings = ISettings()  
        Settings = wrap( settings )
        return Settings

    def SetSettings(self):
        settings = ISettings()  
        Settings = wrap( settings )
        return Settings

IID_IController = pythoncom.MakeIID('{CE9ECC7C-960F-407E-B27B-62E39AB1E30F}')

class Controller:
    """Main Visual Pinball COM interface class."""
    _public_methods_ = [    'Run',
                'Stop',
                'PrintGlobal']
    #_reg_progid_ = "VPinMAME.Controller" #original supplied name conflicts with the visual pinmame dll
    #_reg_clsid_ = "{F389C8B7-144F-4C63-A2E3-246D168F9D39}" #original supplied class id matches vpinmame.dll
    _reg_progid_ = "VPROC.Controller" #rename to Visual PROC Controller
    _reg_clsid_ = "{196FF002-17F9-4714-8A94-A7BD39AD413B}" #use a unique class guid for Visual PROC Controller
    _reg_clsctx_ = pythoncom.CLSCTX_LOCAL_SERVER # LocalSever (no InProc) only means game reloads entirely on next play
    _public_attrs_ = [  'Version',
                'GameName', 
                'Games', 
                'SplashInfoLine',
                'ShowTitle',
                'ShowFrame',
                'ShowDMDOnly',
                'HandleMechanics',
                'HandleKeyboard',
                'DIP',
                'Switch',
                'Mech',
                'Pause',
                'ChangedSolenoids',
                'ChangedGIStrings',
                'ChangedLamps',
                'GetMech',
                'Sys11']
                
    _readonly_attrs_ = [    'Version', 
                'ChangedSolenoids',
                'ChangedLamps',
                'ChangedGIStrings',
                'GetMech']
    
    Version = "22222222"
    ShowTitle = None
    ShowFrame = False
    ShowDMDOnly = False
    HandleKeyboard = False
    DIP = False
    GameName = "Game name"
    switch = [True]*128
    lastSwitch = None
    Pause = None
    Sys11 = False
    ACrelayNumber = 12
    
    game = None
    last_lamp_states = []
    last_coil_states = []
    last_gi_states = []
    
    mechs = {}

    HandleMechanics = True
    GameIsDead = False
    ErrorMsg = "Python Failed -- check the log"

    # Need to overload this method to tell that we support IID_IServerWithEvents
    def _query_interface_(self, iid):
        """ Return this main interface if the IController class is queried. """
        if iid == IID_IController:
            return win32com.server.util.wrap(self)
    
    def PrintGlobal(self):
        """ Unused by pyprocgame. """
        return True
    
    def __checkBridgeOK(self):
        if(self.GameIsDead):
            raise COMException(desc=self.ErrorMsg,scode=winerror.E_FAIL)


    def Run(self, extra_arg=None):
        """ Figure out which game to play based on the contents of the 
        vp_game_map_file. """
        import win32traceutil
        import config

        if(extra_arg is not None):
            logging.getLogger('vpcom').info("Run received extra arg!?")
            logging.getLogger('vpcom').info("Arg was {0}".format(extra_arg))

        vp_game_map_file = config.value_for_key_path(keypath='vp_game_map_file', default='/.')
        vp_game_map = yaml.load(open(vp_game_map_file, 'r'))
        game_class = vp_game_map[self.GameName]['kls']
        game_path = vp_game_map[self.GameName]['path']
        yamlpath = vp_game_map[self.GameName]['yaml']
        logging.getLogger('vpcom').info("S11 is ..." + str(self.Sys11))

        try:
            # switch to the directory of the current game
            curr_file_path = os.path.dirname(os.path.abspath( __file__ ))
            newpath = os.path.realpath(curr_file_path + game_path)
            os.chdir(newpath)

            # add the path to the system path; this lets game relative procgames
            # be found if needed
            sys.path.insert(0, newpath)

            # re-import and re-load config to find game relative config.yaml if existing
            from procgame import config
            config.load()

            # now load procgame --this will be game relative if present, or system-wide if not
            from procgame import *

            # find the class of the game instance
            klass = util.get_class(game_class,game_path)
            self.game = klass()

            self.game.yamlpath = yamlpath
            logging.getLogger('vpcom').info("GameName: " + str(self.GameName))
            logging.getLogger('vpcom').info("SplashInfoLine: " + str(self.SplashInfoLine))

        except Exception, e:
            self.GameIsDead = True
            import traceback
            exc_type, exc_value, exc_traceback = sys.exc_info()

            formatted_lines = traceback.format_exc().splitlines()
            exceptionName =  formatted_lines[-1]

            logging.getLogger('vpcom').info("game instantiation error({0})".format(exceptionName))
            logger = logging.getLogger('vpcom')
            logger.info("PYTHON FAILURE (Visual Pinball Bridge is now broken)")
            logger.info("Exception Name {0}".format(e))
            for l in formatted_lines:
                logger.info("{0}".format(l))
            if(len(formatted_lines) > 2):
                self.ErrorMsg += "\n" + formatted_lines[-3] + "\n" + formatted_lines[-2] + "\n" + formatted_lines[-1]
            raise
        try:
            if(self.game.machine_type is None):
                game_config = yaml.load(open(yamlpath, 'r'))
                self.game.machine_type = game_config['PRGame']['machineType']

            self.last_lamp_states = self.getLampStates()
            self.last_coil_states = self.getCoilStates()

            # Initialize switches.  Call SetSwitch so it can invert
            # normally closed switches as appropriate.
            for i in range(0,120):
                self.SetSwitch(i, False)
        except Exception, e:
            self.GameIsDead = True
            import traceback
            exc_type, exc_value, exc_traceback = sys.exc_info()

            formatted_lines = traceback.format_exc().splitlines()
            exceptionName =  formatted_lines[-1]

            logging.getLogger('vpcom').info("Post-Init Error({0})".format(exceptionName))
            logger = logging.getLogger('vpcom')
            logger.info("PYTHON FAILURE (Visual Pinball Bridge is now broken)")
            logger.info("Exception Name {0}".format(e))
            for l in formatted_lines:
                logger.info("{0}".format(l))
            if(len(formatted_lines) > 2):
                self.ErrorMsg += "\n" + formatted_lines[-3] + "\n" + formatted_lines[-2] + "\n" + formatted_lines[-1]
            raise

        # thread.start_new_thread(self.game.run_loop,(None,exeption_cb))
        thread.start_new_thread(self.RunGame,())

        return True

    def RunGame(self):
        if(self.GameIsDead):
            return
        try:
            self.game.run_loop(.0001)
        except Exception, e:
            import traceback
            exc_type, exc_value, exc_traceback = sys.exc_info()

            #traceback.print_exception(exc_type, exc_value, exc_traceback,
            #                          limit=2, file=sys.stdout)
            #print "*** format_exc, first and last line:"
            formatted_lines = traceback.format_exc().splitlines()
            exceptionName =  formatted_lines[-1]

            ## dump out the details six ways from sunday; 
            ## TODO: choose the one that looks the best an delete the others!
            logger = logging.getLogger('vpcom')
            logger.info("PYTHON FAILURE (Visual Pinball Bridge is now broken)")
            logger.info("Exception Name {0}".format(exceptionName))
            for l in formatted_lines:
                logger.info("{0}".format(l))
            if(len(formatted_lines) > 2):
                self.ErrorMsg += "\n" + formatted_lines[-3] + "\n" + formatted_lines[-2] + "\n" + formatted_lines[-1]
            #raise COMException(desc=self.ErrorMsg,scode=winerror.E_FAIL)

            self.GameIsDead = True
            if(self.game is not None):
                self.game.end_run_loop()
            os._exit(1)
        
    def Stop(self):
        if(self.game is not None):
            self.game.end_run_loop()
        os._exit(1)
        pygame.display.quit()
        pygame.font.quit()
        pygame.quit()
        return 1

    def Games(self, rom_name):
        """ Return the IGames interface, by wrapping the object. """
        games = IGames()
        wrapped_games = wrap (games)
        return wrapped_games

    def SetGames(self, rom_name):
        """ Return the IGames interface, by wrapping the object. """
        games = IGames()
        wrapped_games = wrap (games)
        return wrapped_games
        
    def Switch(self, number):
        """ Return the current value of the requested switch. """
        self.__checkBridgeOK()

        if(self.Sys11 == True) and (number != None):
            number = ((number/8)+1)*10 + number % 8
            
        if number != None: self.lastSwitch = number
        return self.switch[self.lastSwitch]
                
    def SetSwitch(self, number, value):
        """ Set the value of the requested switch. """
        self.__checkBridgeOK()

        # All of the 'None' logic is error handling for unexpected
        # cases when None is passed in as a parameter.  This seems to
        # only happen with the original VP scripts when the switch data
        # is corrupted by making COM calls into this object.  This
        # appears to be a pywin32 bug.

        if value == None: return self.Switch(number)
        if number == None: return self.Switch(number)
        if number != None: self.lastSwitch = number
        self.switch[self.lastSwitch] = value

        if(self.Sys11==True):   
            if self.lastSwitch < 1:
                prNumber = self.VPSwitchDedToPRSwitch(abs(self.lastSwitch))
            elif(self.lastSwitch==82):
                prNumber = pinproc.decode(self.game.machine_type, 'SF1')
            elif(self.lastSwitch == 84):
                prNumber = pinproc.decode(self.game.machine_type, 'SF2')
            elif(self.lastSwitch < 65):
                # number = number -1
                prNumber = (((number/8)+1)*10) + ((number % 8))
                prNumber = self.VPSwitchMatrixToPRSwitch(prNumber)
            else: prNumber = 0
        else:
            if self.lastSwitch < 10:
                prNumber = self.VPSwitchDedToPRSwitch(self.lastSwitch)
            elif self.lastSwitch < 110:
                prNumber = self.VPSwitchMatrixToPRSwitch(self.lastSwitch)
            elif self.lastSwitch < 120:
                prNumber = self.VPSwitchFlipperToPRSwitch(self.lastSwitch)
            else: prNumber = 0


        if not self.game.switches.has_key(prNumber): return False
        if self.game.switches[prNumber].type == 'NC': 
            self.AddSwitchEvent(prNumber, not value)
        else: self.AddSwitchEvent(prNumber, value)

        return True

    def AddSwitchEvent(self, prNumber, value):
        """ Add the incoming VP switch event into the p-roc emulator. """
        # VP doesn't have a concept of bouncing switches; so send
        # both nondebounced and debounced for each event to ensure
        # switch rules for either event type will be processed.
        if value:
            self.game.proc.add_switch_event(prNumber, pinproc.EventTypeSwitchClosedNondebounced)
            self.game.proc.add_switch_event(prNumber, pinproc.EventTypeSwitchClosedDebounced)
        else:
            self.game.proc.add_switch_event(prNumber, pinproc.EventTypeSwitchOpenNondebounced)
            self.game.proc.add_switch_event(prNumber, pinproc.EventTypeSwitchOpenDebounced)
        
    def VPSwitchMatrixToPRSwitch(self, number):
        """ Helper method to find the P-ROC number of a matrix switch. """
        vpNumber = ((number / 10)*8) + ((number%10) - 1)
        vpIndex = vpNumber / 8
        vpOffset = vpNumber % 8 + 1
        if vpIndex < 10:
            switch = 'S' + str(vpIndex) + str(vpOffset)
            return pinproc.decode(self.game.machine_type,switch)
        else: return number
            
    def VPSwitchFlipperToPRSwitch(self, number):
        """ Helper method to find the P-ROC number of a flipper switch. """
        vpNumber = number - 110
        switch = 'SF' + str(vpNumber)
        return pinproc.decode(self.game.machine_type, switch)
        
    def VPSwitchDedToPRSwitch(self, number):
        """ Helper method to find the P-ROC number of a direct switch. """
        vpNumber = number
        switch = 'SD' + str(vpNumber)
        return pinproc.decode(self.game.machine_type, switch)

    def Mech(self, number):
        """ Currently unused.  Game specific mechanism handling will
        be called through this method. """
        self.__checkBridgeOK()
        return True

    def SetMech(self, number):
        """ Currently unused.  Game specific mechanism handling will
        be called through this method. """
        self.__checkBridgeOK()
        return True

    def SetMech(self, number, args):
        """ Currently unused.  Game specific mechanism handling will
        be called through this method. """
        self.__checkBridgeOK()
        
        if(self.GameName=="t2_l8"):
            self.SetSwitch(33, True) # gun is home...
            # MECHGUN.MType=vpmMechOneSol+vpmMechReverse+vpmMechLinear
            #   MECHGUN.Sol1=11
            #   MECHGUN.Length=200
            #   MECHGUN.Steps=41
            #   MECHGUN.AddSw 32,27,27 'Gun Mark
            #   MECHGUN.AddSw 33,0,0 'Gun Home start position
            #   MECHGUN.Callback=GetRef("UpdateGun")
            #   MECHGUN.Start
        return True

    pos = 0
    direction = 1   
    cnt = 0
    def GetMech(self, number):
        """ Currently unused.  Game specific mechanism handling will
        be called through this method. """
        self.__checkBridgeOK()

        if(self.GameName=="t2_l8"):
            # if the coil associated with this mech is on
            if(self.game.proc.drivers[pinproc.decode(self.game.machine_type, "C11")].curr_state == True) :
                # check the direction
                self.game.logging_enabled = True
                logging.getLogger('vpcom').info("Coil # %d " % number )
                if(self.direction == 1):
                    self.pos = self.pos + .5
                    if(self.pos >= 41):
                        self.direction = -1
                else:
                    self.pos = self.pos - .5
                    if(self.pos <= 0):
                        self.direction = 1
                if(self.pos == 0):
                    self.SetSwitch(33, True)
                elif(self.pos == 1):
                    self.SetSwitch(33, False)
                elif(self.pos == 27):
                    self.SetSwitch(32, True)
                elif((self.pos == 28) or (self.pos == 26)):
                    self.SetSwitch(32, False)
            return self.pos
        return 0

    def ChangedSolenoids(self):
        """ Return a list of changed coils. """
        self.__checkBridgeOK()

        coils = self.getCoilStates()
        changedCoils = []
        
        already=False
        if len(self.last_coil_states) > 0:
            for i in range(0,len(coils)):
                if coils[i] != self.last_coil_states[i]:
                    if not already:
                        changedCoils += [(0,True)]
                        already = True
                    changedCoils += [(i,coils[i])]
                
        self.last_coil_states = coils
        return changedCoils
        
    def ChangedLamps(self):
        """ Return a list of changed lamps. """
        self.__checkBridgeOK()

        lamps = self.getLampStates()
        changedLamps = []
        
        if len(self.last_lamp_states) > 0:
            for i in range(0,len(lamps)):
                if lamps[i] != self.last_lamp_states[i]:
                    changedLamps += [(i,lamps[i])]
                
        self.last_lamp_states = lamps
        return changedLamps

    def ChangedGIStrings(self):
        """ Return a list of changed GI strings. """
        self.__checkBridgeOK()

        gi = self.getGIStates()
        changedGI = []

        if len(self.last_gi_states) > 0:
            for i in range(0,len(gi)):
                if gi[i] != self.last_gi_states[i]:
                    changedGI += [(i,gi[i])]

        self.last_gi_states = gi
        return changedGI
            
    def getGIStates(self):
        """ Gets the current state of the GI strings. """
        self.__checkBridgeOK()

        vpgi = [False]*5
    
        for i in range(0,5):
            numStr = 'G0' + str(i+1)
            prNumber = pinproc.decode(self.game.machine_type, numStr)
            vpgi[i] = self.game.proc.drivers[prNumber].curr_state
            
        return vpgi
        
    def getLampStates(self):
        """ Gets the current state of the lamps. """
        self.__checkBridgeOK()

        vplamps = [False]*90

        if(self.Sys11 == False):    
            for i in range(0,64):
                vpNum = (((i/8)+1)*10) + (i%8) + 1
                vplamps[vpNum] = self.game.proc.drivers[i+80].curr_state
        else:
            for i in range(0,64):
                vpNum = i+1
                vplamps[vpNum] = self.game.proc.drivers[i+80].curr_state                    
        return vplamps
        
    def getCoilStates(self):
        """ Gets the current state of the coils. """
        self.__checkBridgeOK()

        pycoils = self.game.proc.drivers
        vpcoils = [False]*64
    
        if(self.Sys11 == True):
            ACState = pycoils[12+39].curr_state

        for i in range(0,len(vpcoils)):

            if i < 33:
                if(self.Sys11!=True):
                    if i<=28: vpcoils[i] = pycoils[i+39].curr_state
                    elif i<=32: vpcoils[i] = False # Unused?

                else: # do the relay lying here...
                    if i<=8: vpcoils[i] = pycoils[i+39].curr_state and (ACState == False)
                    elif i<=24: vpcoils[i] = pycoils[i+39].curr_state
                    elif i<=32: vpcoils[i] = pycoils[i+39].curr_state and (ACState == True)

            # Use the machine's Hold coils for the VP flippers
            # since they stay on until the button is released
            elif i == 34: vpcoils[i] = pycoils[pinproc.decode(self.game.machine_type, "FURH")].curr_state
            elif i == 36: vpcoils[i] = pycoils[pinproc.decode(self.game.machine_type, "FULH")].curr_state
            elif i<44:
                if self.game.machine_type == pinproc.MachineTypeWPC95:
                    vpcoils[i] = pycoils[i+31].curr_state
                else: vpcoils[i] = pycoils[i+107].curr_state
            elif i == 46: vpcoils[i] = pycoils[pinproc.decode(self.game.machine_type, "FLRH")].curr_state
            elif i == 48: vpcoils[i] = pycoils[pinproc.decode(self.game.machine_type, "FLLH")].curr_state
            else: vpcoils[i] = pycoils[i+108].curr_state

        return vpcoils      
            
        
def Register(pyclass=Controller, p_game=None):
    """ Registration code for the Visual Pinball COM interface for pyprocgame."""
    pythoncom.CoInitialize()
    from win32com.server.register import UseCommandLine
    UseCommandLine(pyclass)
    
# Run the registration code by default.  Using the commandline param
# "--unregister" will unregister this COM object.
if __name__=='__main__':
    Register(Controller)
