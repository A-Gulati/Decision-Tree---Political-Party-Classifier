class Node:
  def __init__(self):
    self.label = None #attribute being tested
    self.children = {}
    #-------------------
    #self.posexamples = []
    #self.negexamples = []
    self.pval = None #pval stores the value of the previous attribute that lead to this split
    self.answer = None #output of node
    self.modeclass = None #store the mode of the examples - used in pruning

  def addchildren(self,value,child):
    self.children.update({value : child})
