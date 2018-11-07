from node import Node
import math
from copy import deepcopy

'''
Takes in an array of examples, and returns a tree (an instance of Node)
trained on the examples.  Each example is a dictionary of attribute:value pairs,
and the target class variable is a special attribute with the name "Class".
Any missing attributes are denoted with a value of "?"
'''
def ID3(examples, default):
    examples = corrector(examples) #replace all missing attributes with some value
    if not examples:
        #print("examples was empty")
        rval = Node()
        rval.label = default
        rval.answer = default
        return rval

    #create a list of all unique attributes in examples
    all_keys = set().union(*(d.keys() for d in examples))
    all_keys.remove('Class')

    #triv flag is true when all attributes have the same value
    #ie no non trivial splits are possible
    i = 0
    triv = False
    for x in all_keys:
        att_values = list(set(d[x] for d in examples))
        if len(att_values) == 1: i += 1
    if i == len(all_keys):
        triv = True

    #if either no non trivial splits are possible or all classifications are the same
    #return a node with label equal to the most common classification
    if ((find_entropy(examples) == 0) or triv):
        #print("trivial splits or same classification")
        rval = Node()
        rval.label = default
        rval.answer = modeclass(examples)
        #store modeclass
        rval.modeclass = modeclass(examples)
        return rval

    else:

        #create a list of all unique attributes
        all_keys = set().union(*(d.keys() for d in examples))
        all_keys.remove('Class')

        #find the best attribute to split on
        maxgain = 0
        bestatt = None
        for att in all_keys:
            if (find_gain(examples,att) > maxgain):
                maxgain = find_gain(examples,att)
                bestatt = att
            else:
                continue
            #in the case that the gain was zero for all of the attributes,
            #assign to bestatt the first attribute whose values are not homogenous
        if bestatt == None:
            for att in all_keys:
                a_values = list(set(d[att] for d in examples if att is not None))
                if len(a_values) != 1:
                    bestatt = att
                    break
        #if the previous loop couldnt find an att with non homogenous values
        #assign the first att to bestatt since it doesnt matter and we're all alone in the universe
        if bestatt == None:
            for att in all_keys:
                bestatt = att
                break

        #create a node that will be the root of a subtree with attribute
        new_root = Node()
        new_root.label = bestatt
        #store modeclass
        new_root.modeclass = modeclass(examples)
        #find all unique attribute values - added if statement to account for empty labels
        att_values = list(set(d[new_root.label] for d in examples if new_root.label is not None))

        #iterate over each possible attribute outcome
        #create list of all examples where attribute has that outcome
        #create subtree and recursively call id3 to build out the tree
        for v in att_values:
            subset = [d for d in examples if d[new_root.label] == v]
            new_root.addchildren(v,ID3(subset,v))
    return new_root

'''
Takes in a trained tree and a validation set of examples.  Prunes nodes in order
to improve accuracy on the validation data; the precise pruning strategy is up to you.
'''
def prune(node, examples):
    #print("prune was run")
    everynode = []
    everynode.append(node)
    count = 0
    while not(everynode==[]):
        count+=1
        testnode = everynode.pop(0)
        #unpruned stores the accuracy with the node
        unpruned = test(testnode,examples)
        #copy the node we want to test
        copynode = deepcopy(testnode)
        #prune the node by cutting off the branches below this node, setting the node to its mode
        copynode.children = {}
        copynode.answer = copynode.modeclass
        #pruned stores the accuracy without the node
        pruned = test(copynode,examples)
        #if the pruned accuracy was better than unpruned, prune testnode
        if pruned > unpruned:
            #print("pruning was effective")
            testnode.answer = testnode.modeclass
            testnode.children = {}
            return node

        for child in testnode.children:
            #print("len(everynode)",len(everynode))
            everynode.append(node.children[child])

        #stops this loop if it runs for too long
        if count > 100:
            #return node
            break
        continue

    return node


'''
Takes in a trained tree and a test set of examples.  Returns the accuracy (fraction
of examples the tree classifies correctly).
'''
def test(node, examples):
    myg = [evaluate(node,testcase) for testcase in examples]
    actual = [d["Class"] for d in examples]
    correct = 0
    for i in range(len(examples)):
        if myg[i] == actual[i]:
            correct+=1
    return correct/(len(examples))

'''
Takes in a tree and one example.  Returns the Class value that the tree
assigns to the example.
'''
def evaluate(node, example):
    if node.children == {}:
        if node.answer is not None:
            return node.answer
        else:
            return #return nothing if there is no answer and no children
    else:
        mykey = example[node.label]
        if mykey in node.children:
        #if node.children[]:
            return evaluate(node.children[example[node.label]],example)
        #if the key in example is not in children, return answer
        else:
            return node.answer


#Helper functions:

def find_entropy(data): #pass a subset of training examples and the target attribute to measure
    classes = list(set(d['Class'] for d in data)) #list of unique classes in list
    classcounts = []
    for c in classes:
        classcounts.append(sum([d['Class'] == c for d in data]))

    H=0
    for i in classcounts:
        if i == 0:
            continue
        else:
            H -= (i/sum(classcounts))*math.log(i/sum(classcounts),2)
    return H

def find_gain(data,att): #pick an attribute to see the gain if we split on that attribute
    ent_total = find_entropy(data) #entropy of the whole lst of dicts
    unique_vals = list(set([d[att] for d in data])) #create a list of unique values corresponding to a certain attribute
    fullset = []
    for val in unique_vals:
        subset = []
        for dic in data:
            if dic[att] == val:
                subset.append(dic)
        fullset.append(subset)

    temp = 0
    for lstofexamples in fullset:
        temp -= (len(lstofexamples)/len(data))*find_entropy(lstofexamples)

    G = ent_total + temp
    return G

#returns the most frequent class label
def modeclass(data):
    all_classes = [d['Class'] for d in data]

    freq = {}
    for classval in all_classes:
        freq[classval] = freq.get(classval,0)+1

    sorted_array = sorted(freq, key=lambda x: (-freq[x], x))
    #print("sorted array in modeclass:",sorted_array)
    return sorted_array[0]

def corrector(examples):
    #print("corrector was run")
    if(isinstance(examples, dict)):
        for k,v in examples.items():
            if v == '?':
                examples[k]=rep(k,examples)
    else:
        for d in examples:
            #store all keys where value is unknown
            unknowns = [k for k,v in d.items() if v == '?']
            for k in unknowns:
                replacement = rep(k,examples)
                d[k] = replacement
                #print("corrected a ?")

    return examples

def rep(key,examples):
    if(isinstance(examples, dict)):
        for k,v in examples.items():
            if v!='?':
                return v
    for d in examples:
        for k,v in d.items():
            if (k == key)and(not(v=='?')):
                return v
            else:
                continue
