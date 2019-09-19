1. Overall design
    Implemented a hierarchy of node types. Including following classes:

     
                                                              node
                                                        /              \
                                                       /                \
                                                    leaf              nonLeaf
                                                  /      \            /     \   
                                                 /        \          /       \
                                               task    condition  composite  decorator
                                                                   /           \
                                                                  /             \
                                      sequence, selection, priority              logicalNegation, untilFail, timer                


    node:
        status: To describe the status of that node in the whole behaviour tree.
        reset(): To reset its own status.

    nonLeaf:
        children: A list to stored all its children nodes.
        addChild(): Add child.
        reset(): Override. Reset all children recursively.

    composite:
        findLastRunning(): Find if there has any RUNNING node in previous call.
    
    decorator:
        run(): Check if decorator has one child or not.

    priority:
        run(): Override. Return FAILED if all children FAILED. If child's status is FAILED, continue the loop, otherwise,
                return child's status. When return FAILED or SUCCEEDED, call self.reset().
        reset(): Override. Because priority is root in this problem, make sure reset BLACKBOARD['COUNT'] to 0

    sequence:
        run(): Override. Check if has lastRunning node. If has, start from that node, otherwise start from the leftmost child. 
                Return SUCCEEDED if all children SUCCEEDED. If child's status is SUCCEEDED, continue the loop, otherwise,
                return child's status. When return FAILED or SUCCEEDED, call self.reset().
        reset(): Override. Because priority is root in this problem, make sure reset BLACKBOARD['COUNT'] to 0

    selection:
        run(): Override. Check if has lastRunning node. If has, start from that node, otherwise start from the leftmost child.
                Other are the same as priority.
    
    timer:
        time: Attribute of Timer node.
        run(): Override. Check if BLACKBOARD['COUNT'] is less than self.time. If it is, incrementing BLACKBOARD['COUNT'] and
                return RUNNING, otherwise reset BLACKBOARD['COUNT'] to 0, call self.reset() and return SUCCEEDED.

    untilFail:
        run(): Override. Check if child's status is FAILED. If it is, call self.reset() and return SUCCEEDED, otherwise return
                RUNNING.
    
    logicalNegation:
        run(): Override. If child's status is SUCCEEDED or FAILED, call self.reset() and return opposite result, otherwise return
                RUNNING.

2. About specific tasks
    Task dock would recharge battery, set BLACKBOARD['BATTERY_LEVEL'] to 100.
    Task cleanSpot would cost 1 unit of enery everytime it's called.
    Task doneSpot, doneGeneral and clean would cost 2 unit2 of enery everytime they're called.
    Task findHome would set BLACKBOARD['HOME_PATH'] to "A PATH TO HOME".
    Task doneSpot would set BLACKBOARD['SPOT'] to False.
    Task doneGeneral would set BLACKBOARD['GENERAL'] to False.
    
3. When running program
    Default BLACKBOARD['BATTERY_LEVEL'] is 100. When you first into progam, it would let you input SPOT and GENERAL to set 
    BLACKBOARD['SPOT'] and BLACKBOARD['GENERAL']. When finally status become SUCCEEDED, it would let you choose start a new
    work from current state or exit. Everytime when you choose to continue, you should set SPOT and GENERAL again, but notice that
    BLACKBOARD['BATTERY_LEVEL'] would not change.