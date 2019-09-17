import sys

###############################
## Behavior Tree Definations ##
###############################


###### Required Variables #####

# Blackboard objects
BLACKBOARD = {
	"BATTERY_LEVEL": 100,
	"SPOT": True,
	"GENERAL": True,
	"DUSTY_SPOT": True,
	"HOME_PATH": "DEFAULT PATH BACK TO HOME",
	}

# Status
class STATUS():
	FAILED = -1
	SUCCEEDED = 0
	RUNNING = 1


#### Node class definitions ###

# Node
# -- children: node or derived class instance
# -- weight: used by priority composite
# -- time: duration
class node(object):
	def __init__(self, children = None, status = None, weight = 1, time = 0):
		if children == None:
			self.children = list()
		else:
			self.children = children
		self.status = status
		self.weight = weight
		self.time = time

	def addChild(self, child):
		if not child is None:
			self.children.append(child)

# Task
class task(node):
	def __init__(self, children = None, status = None, weight = 1, time = 0, input = None):
		super(task, self).__init__(children, status, weight, time)
		self.input = input                              # some tasks may have an input (assume only 1)

        def run(self):                                  # task node has no child
		assert self.children.__len__ == 0

# Condition
class condition(node):
	def run(self):                                      # condition node has no child
		assert self.children.__len__ == 0                   

# Composite
class composite(node):
	pass

# Decorator
class decorator(node):
	def run(self):
		assert self.children.__len__ == 1               # each decorator would only have one child
		assert self.children[0].time == 0               # time in attached child should be 0

# Task -- FIND HOME
class findHome(task):
	def run(self):
		super(findHome, self).run()
		BLACKBOARD['HOME_PATH'] = "A PATH TO HOME"      # simulate finding a path to home and store it to BALCKBOARD
		self.status = STATUS.SUCCEEDED;
		return self.status

# Task -- GO HOME
class goHome(task):
	def run(self):
		super(goHome, self).run()
		self.status = STATUS.SUCCEEDED;
		return self.status

# Task -- DO NOTHING
class doNothing(task):
	def run(self):
		super(doNothing, self).run()
		self.status = STATUS.SUCCEEDED;
		return self.status
	
# Task -- DOCK
class dock(task):
	def run(self):
		super(dock, self).run()
		self.status = STATUS.SUCCEEDED;
		return self.status

# Task -- CLEAN SPOT
class cleanSpot(task):
	def run(self):
		super(cleanSpot, self).run()
		self.status = STATUS.SUCCEEDED;
		return self.status

# Task -- DONE SPOT
class doneSpot(task):
	def run(self):
		super(doneSpot, self).run()
		BLACKBOARD['SPOT'] = False                      # SPOT in BALCKBOARD turns to FALSE
		print("DONE SPOT!")
		self.status = STATUS.SUCCEEDED;
		return self.status

# Task -- DONE GENERAL
class doneGeneral(task):
	def run(self):
		super(doneGeneral, self).run()
		BLACKBOARD['GENERAL'] = False                   # GENERAL in BALCKBOARD turns to FALSE
		print("DONE GENERAL!")
		self.status = STATUS.SUCCEEDED;
		return self.status

# Task -- CLEAN
class clean(task):
	def run(self):
		super(clean, self).run()
		self.status = STATUS.SUCCEEDED;
		return self.status

# Condition -- BATTERY < 30%
class batteryLessThan30(condition):
	def run(self):
		super(batteryLessThan30, self).run()
		if BLACKBOARD['BATTERY_LEVEL'] < 30:
			self.status = STATUS.SUCCEEDED
		else:
			self.status = STATUS.FAILED
		return self.status

# Condition -- GENERAL
class generalCondition(condition):
	def run(self):
		super(generalCondition, self).run()
		if BLACKBOARD['GENERAL']:
			self.status = STATUS.SUCCEEDED
		else:
			self.status = STATUS.FAILED
		return self.status

# Condition -- SPOT
class spotCondition(condition):
	def run(self):
		super(spotCondition, self).run()
		if BLACKBOARD['SPOT']:
			self.status = STATUS.SUCCEEDED
		else:
			self.status = STATUS.FAILED
		return self.status

# Condition -- DUSTY SPOT
class dustySpotCondition(condition):
	def run(self):
		super(dustySpotCondition, self).run()
		if BLACKBOARD['DUSTY_SPOT']:
			self.status = STATUS.SUCCEEDED
		else:
			self.status = STATUS.FAILED
		return self.status

# Sequence -- derived from composite
class sequence(composite):
	def run(self):
		for child in self.children:
			child.status = child.run()
			if child.status == STATUS.SUCCEEDED:
				continue;                               # if SUCCEEDED, continue and check others
			elif child.status == STATUS.FAILED:
				return STATUS.FAILED                    # anyone FAILED, return FAILED
			else:
				while child.status == STATUS.RUNNING:
					continue                            # if RUNNING, continue the loop
				if child.status == STATUS.SUCCEEDED:
					continue
				elif child.status == STATUS.FAILED:
					return STATUS.FAILED
		return STATUS.SUCCEEDED                         # if no one FAILED, return SUCCEEDED

# Selection -- derived from composite
class selection(composite):
	def run(self):
		for child in self.children:
			child.status = child.run()
			if child.status == STATUS.SUCCEEDED:
				return STATUS.SUCCEEDED                 # anyone SUCCEEDED, return SUCCEEDED
			elif child.status == STATUS.FAILED:
				continue                                # if FAILED, continue and check others
			else:
				while child.status == STATUS.RUNNING:
					continue                            # if RUNNING, continue the loop
				if child.status == STATUS.SUCCEEDED:
					return STATUS.SUCCEEDED
				elif child.status == STATUS.FAILED:
					continue
		return STATUS.FAILED                            # if no one SUCCEEDED, return FAILED

# Priority -- derived from composite
class priority(composite):
	def run(self):
        #self.children.sort(key = lambda x: x.)
		for child in self.children:
			child.status = child.run()
			if child.status == STATUS.SUCCEEDED:
				return STATUS.SUCCEEDED                 # anyone SUCCEEDED, return SUCCEEDED
			elif child.status == STATUS.FAILED:
				continue                                # if FAILED, continue and check others
			else:
				while child.status == STATUS.RUNNING:
					continue                            # if RUNNING, continue the loop
				if child.status == STATUS.SUCCEEDED:
					return STATUS.SUCCEEDED
				elif child.status == STATUS.FAILED:
					continue
		return STATUS.FAILED                            # if no one SUCCEEDED, return FAILED

# LogicalNegation -- derived from decorator
class logicalNegation(decorator):
	def run(self):
		super(logicalNegation, self).run()
		attached = self.children[0]
		status = attached.run()
		if status == STATUS.SUCCEEDED:                  # negates result
			attached.status = STATUS.FAILED
		elif status == STATUS.FAILED:
			attached.status = STATUS.SUCCEEDED          # negates result
		return attached.status

# UntilFail -- derived from decorator
class untilFail(decorator):
	def run(self):
		super(untilFail, self).run()
		attached = self.children[0]
		while attached.status != STATUS.FAILED:         # executes the attached node until FAILED
			attached.status = attached.run()
		return STATUS.SUCCEEDED

# Timer -- derived from decorator
class timer(decorator):
	def __init__(self, children = None, status = None, weight = 1, time = 0, maxTime = None):
		super(timer, self).__init__(children, status, weight, time)
		self.maxTime = maxTime

	def run(self):
		super(timer, self).run()
		attached = self.children[0]
		while attached.time < self.maxTime - 1:
			attached.run()
			attached.time += 1                         # Suppose each node run 1s
			attached.status = STATUS.RUNNING

		# last round
		attached.status = attached.run()               # status is last round's status
		attached.time = 0
		return attached.status


		
###############################
##### Main program entry ######
###############################	

if __name__ == '__main__':

	####### init all nodes #######

	# tasks
	T_doNothing = doNothing(None, None, 3, 0)
	T_findHome = findHome()
	T_goHome = goHome()
	T_dock = dock()
	T_cleanSpot = cleanSpot()
	T_doneSpot = doneSpot()
	T_doneGeneral = doneGeneral()
	T_clean = clean()

	# conditions
	C_batteryLessThan30 = batteryLessThan30()
	C_general = generalCondition()
	C_spot = spotCondition()
	C_dustySpot = dustySpotCondition()

	# composites
	Sq_home = sequence(None, None, 1, 0)
	Sq_general = sequence()
	Sq_spot = sequence()
	Sq_doneGeneral = sequence()
	Sq_battery = sequence()
	Sq_dustySpot = sequence()

	Sl_clean = selection(None, None, 2, 0)
	Sl_dustySpot = selection()

	P_root = priority()

	# decorators
	D_logicalNegation = logicalNegation()
	D_untilFill = untilFail()
	D_timer20 = timer(None, None, 0, 0, 20)
	D_timer35 = timer(None, None, 0, 0, 35)


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
	D_timer35.addChild(T_cleanSpot)

	############## test #############
	while(1):
		BLACKBOARD = {
			"BATTERY_LEVEL": 100,
			"SPOT": True,
			"GENERAL": True,
			"DUSTY_SPOT": True,
			"HOME_PATH": "DEFAULT PATH BACK TO HOME",
			}

		print("Creating A new job now.")
		S = int(input("Spot status: input 0 for False, input 1 for True: "))
		if S == 0:
			BLACKBOARD['SPOT'] = False
			
		G = int(input("General status: input 0 for False, input 1 for True: "))
		if G == 0:
			BLACKBOARD['GENERAL'] = False


		count = 5
		for i in range(count):
			BLACKBOARD['BATTERY_LEVEL'] = int(input("BATTERY LEVEL is: "))
			print(BLACKBOARD)
			root = P_root
			root.run()

            # TODO: should have a break point when doing nothing
            # sys.exit()

