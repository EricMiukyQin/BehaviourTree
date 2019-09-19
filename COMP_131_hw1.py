# Blackboard objects
BLACKBOARD = {
    "BATTERY_LEVEL": 100,
    "SPOT": True,
    "GENERAL": True,
    "DUSTY_SPOT": True,
    "HOME_PATH": "DEFAULT PATH BACK TO HOME",
    "COUNT": 0  # used for timer
    }

# Status
class STATUS():
    FAILED = 0
    SUCCEEDED = 1
    RUNNING = 2

# node
class node(object):
    def __init__(self):
        self.status = None

    def reset(self):
        self.status = None

# leaf node
class leaf(node):
    pass

# non-leaf node
# before return SUCCEEDED or FAILED, reset all children recursively
class nonLeaf(node):
    def __init__(self, children = None):
        super(nonLeaf, self).__init__()
        
        if children is None:
            children = list()

        self.children = children

    def addChild(self, child):
        if not child is None:
            self.children.append(child)
 
    def reset(self):
        super(nonLeaf, self).reset()
        for child in self.children:
            child.reset()

# task
class task(leaf):
    pass

# condition
class condition(leaf):
    pass

# composite
class composite(nonLeaf):
    # find if has last RUNNING child
    def findLastRunning(self):
        lastRunning = False
        lastRunningIdx = 0
        for child in self.children:
            if child.status == STATUS.RUNNING:
                lastRunning = True
                lastRunningIdx = self.children.index(child)
                break
        return lastRunning, lastRunningIdx

# decorator
# each would only have one child
class decorator(nonLeaf):
    def run(self):
        assert self.children.__len__() == 1

# Priority
# every time start from weight 1
# because priority is root in this problem, so we need to reset BLACKBOARD['COUNT'] to 0
class priority(composite):
    def run(self):
        for child in self.children:
            child.status = child.run()
            if child.status != STATUS.FAILED:
                if child.status == STATUS.SUCCEEDED:
                    self.reset()
                    return STATUS.SUCCEEDED
                else:
                    return STATUS.RUNNING
        self.reset()
        return STATUS.FAILED

    def reset(self):
        super(priority, self).reset()
        BLACKBOARD['COUNT'] = 0

# Sequence
# if has last RUNNING child, from it; else from left
class sequence(composite):
    def run(self):
        lastRunning, startIdx = self.findLastRunning()
        if not lastRunning:
            startIdx = 0

        for child in self.children[startIdx:]:
            child.status = child.run()
            if child.status != STATUS.SUCCEEDED:
                if child.status == STATUS.FAILED:
                    self.reset()
                    return STATUS.FAILED
                else:
                    return STATUS.RUNNING
        self.reset()
        return STATUS.SUCCEEDED

# Selector
# if has last running child, from it; else from left
class selection(composite):
    def run(self):
        lastRunning, startIdx = self.findLastRunning()
        if not lastRunning:
            startIdx = 0
            
        for child in self.children[startIdx:]:
            child.status = child.run()
            if child.status != STATUS.FAILED:
                if child.status == STATUS.SUCCEEDED:
                    self.reset()
                    return STATUS.SUCCEEDED
                else:
                    return STATUS.RUNNING
        self.reset()
        return STATUS.FAILED

# Timer
class timer(decorator):
    def __init__(self, children = None, time = None):
        super(timer, self).__init__(children)
        self.time = time

    def run(self):
        super(timer, self).run()
        child = self.children[0]

        if BLACKBOARD['COUNT'] < self.time:
            BLACKBOARD['COUNT'] += 1
            child.status = child.run()
            return STATUS.RUNNING
        else:
            BLACKBOARD['COUNT'] = 0
            self.reset()
            return STATUS.SUCCEEDED

# Until Fail
class untilFail(decorator):
    def run(self):
        super(untilFail, self).run()
        child = self.children[0]
        child.status = child.run()
        if child.status != STATUS.FAILED:
            return STATUS.RUNNING
        else:
            self.reset()
            return STATUS.SUCCEEDED

# Logical negation
class logicalNegation(decorator):
    def run(self):
        super(logicalNegation, self).run()
        child = self.children[0]
        child.status = child.run()
        if child.status == STATUS.SUCCEEDED:
            self.reset()
            return STATUS.FAILED
        elif child.status == STATUS.FAILED:
            self.reset()
            return STATUS.SUCCEEDED
        else:
            return STATUS.RUNNING
                
# Task -- FIND HOME
# simulate finding a path to home and store it to BALCKBOARD
class findHome(task):
    def run(self):
        print("Find home")
        BLACKBOARD['HOME_PATH'] = "A PATH TO HOME"
        return STATUS.SUCCEEDED

# Task -- GO HOME
class goHome(task):
    def run(self):
        print("Go home")
        return STATUS.SUCCEEDED

# Task -- DO NOTHING
class doNothing(task):
    def run(self):
        print("Do nothing")
        return STATUS.SUCCEEDED

# Task -- DOCK
# charge to full battery level
class dock(task):
    def run(self):
        print("Dock")
        BLACKBOARD['BATTERY_LEVEL'] = 100
        return STATUS.SUCCEEDED

# Task -- CLEAN SPOT
# BATTERY_LEVEL - 1
class cleanSpot(task):
    def run(self):
        print("Clean spot")
        BLACKBOARD['BATTERY_LEVEL'] -= 1
        return STATUS.SUCCEEDED

# Task -- DONE SPOT
# BATTERY_LEVEL - 2
# SPOT in BALCKBOARD turns to FALSE
class doneSpot(task):
    def run(self):
        BLACKBOARD['BATTERY_LEVEL'] -= 2
        BLACKBOARD['SPOT'] = False
        print("DONE SPOT!")
        return STATUS.SUCCEEDED

# Task -- DONE GENERAL
# BATTERY_LEVEL - 2
# GENERAL in BALCKBOARD turns to FALSE
class doneGeneral(task):
    def run(self):
        BLACKBOARD['BATTERY_LEVEL'] -= 2
        BLACKBOARD['GENERAL'] = False
        print("DONE GENERAL!")
        return STATUS.SUCCEEDED

# Task -- CLEAN
# BATTERY_LEVEL - 2
class clean(task):
    def run(self):
        BLACKBOARD['BATTERY_LEVEL'] -= 2
        return STATUS.SUCCEEDED

# Condition -- BATTERY < 30%
class batteryLessThan30(condition):
    def run(self):
        if BLACKBOARD['BATTERY_LEVEL'] < 30:
            return STATUS.SUCCEEDED
        else:
            return STATUS.FAILED

# Condition -- GENERAL
class generalCondition(condition):
    def run(self):
        if BLACKBOARD['GENERAL']:
            return STATUS.SUCCEEDED
        else:
            return STATUS.FAILED

# Condition -- SPOT
class spotCondition(condition):
    def run(self):
        if BLACKBOARD['SPOT']:
            return STATUS.SUCCEEDED
        else:
            return STATUS.FAILED

# Condition -- DUSTY SPOT
class dustySpotCondition(condition):
    def run(self):
        if BLACKBOARD['DUSTY_SPOT']:
            return STATUS.SUCCEEDED
        else:
            return STATUS.FAILED

def buildBT():
    # tasks
    T_doNothing = doNothing()
    T_findHome = findHome()
    T_goHome = goHome()
    T_dock = dock()
    T_cleanSpot = cleanSpot()
    T_doneSpot = doneSpot()
    T_doneGeneral = doneGeneral()
    T_clean = clean()
    T_cleanDustySpot = cleanSpot()

    # conditions
    C_batteryLessThan30 = batteryLessThan30()
    C_general = generalCondition()
    C_spot = spotCondition()
    C_dustySpot = dustySpotCondition()

    # composites
    Sq_home = sequence()
    Sq_general = sequence()
    Sq_spot = sequence()
    Sq_doneGeneral = sequence()
    Sq_battery = sequence()
    Sq_dustySpot = sequence()

    Sl_clean = selection()
    Sl_dustySpot = selection()

    P_root = priority()

    # decorators
    D_logicalNegation = logicalNegation()
    D_untilFill = untilFail()
    D_timer20 = timer(None, 20)
    D_timer35 = timer(None, 35)


    ########### build tree ##########
    P_root.addChild(Sq_home)
    P_root.addChild(Sl_clean)
    P_root.addChild(T_doNothing)

    Sq_home.addChild(C_batteryLessThan30)
    Sq_home.addChild(T_findHome)
    Sq_home.addChild(T_goHome)
    Sq_home.addChild(T_dock)

    Sl_clean.addChild(Sq_spot)
    Sl_clean.addChild(Sq_general)

    Sq_spot.addChild(C_spot)
    Sq_spot.addChild(D_timer20)
    Sq_spot.addChild(T_doneSpot)
    D_timer20.addChild(T_cleanSpot)

    Sq_general.addChild(C_general)
    Sq_general.addChild(Sq_doneGeneral)

    Sq_doneGeneral.addChild(D_untilFill)
    Sq_doneGeneral.addChild(T_doneGeneral)
    D_untilFill.addChild(Sq_battery)

    Sq_battery.addChild(D_logicalNegation)
    D_logicalNegation.addChild(C_batteryLessThan30)
    Sq_battery.addChild(Sl_dustySpot)

    Sl_dustySpot.addChild(Sq_dustySpot)
    Sl_dustySpot.addChild(T_clean)

    Sq_dustySpot.addChild(C_dustySpot)
    Sq_dustySpot.addChild(D_timer35)
    D_timer35.addChild(T_cleanDustySpot)

    return P_root


if __name__ == '__main__':
    # test

    root = buildBT()
    status = None

    while(1):
        if status is None or status == STATUS.SUCCEEDED:
            SPOT = int(input("Spot: input 0 for False, 1 for True: "))
            if SPOT == 0:
                BLACKBOARD['SPOT'] = False
            else:
                BLACKBOARD['SPOT'] = True
            GENERAL = int(input("General: input 0 for False, 1 for True: "))
            if GENERAL == 0:
                BLACKBOARD['GENERAL'] = False
            else:
                BLACKBOARD['GENERAL'] = True

        status = root.run()
        if status == STATUS.SUCCEEDED:
            print("SUCCEEDED! Now BLACKBOARD is: ")
            print(BLACKBOARD)
            if str(input("Work is done, do you want to exit?\n(y or n) y for Yes, n for No: ")) == 'y':
                break;