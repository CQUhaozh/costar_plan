
# By Chris Paxton
# (c) 2017 The Johns Hopkins University
# See License for more details

from node import Node

from costar_task_plan.abstract import *

import operator
import numpy as np

'''
Basic policies object. This takes a set of other objects which are themselves
just parameterized functions and uses them to perform a tree search.

The basic use case is to instantiate the object with your preferered functions
for initialization, sampling order, rollouts, scoring, widening, etc., and call
the "explore(root)" function until time is up.

Then you can extract() with the provided extraction function.

We also provide a "getNext()" function, which is somewhat experimental: this
function is used in some of the OpenAI gym environments as a way to get the
next point where a decision needs to be made.
'''


class AbstractMctsPolicies(object):

    def __init__(self,
                 score,
                 extract,
                 widen,
                 initialize=None,
                 sample=None,
                 rollout=None,
                 max_depth=10,
                 verbose=0,
                 dfs=False):
        self.max_depth = max_depth
        self._rollout = rollout
        self._initialize = initialize
        self.sample = sample
        self._score = score
        self._widen = widen
        self._extract = extract
        self._dfs = dfs
        self.verbose = verbose

        if self.verbose > 0:
            print "=========================================="
            print "SUMMARY OF MCTS OPTIONS"
            print "-----------------------"
            print "ROLLOUT:", rollout
            print "INITIALIZE:", initialize
            print "SAMPLE:", sample
            print "SCORE:", score
            print "WIDEN:", widen
            print "=========================================="

        self._can_widen = self.sample is not None and self._widen is not None

    def select(self, node, max_depth=10, can_widen=True):
        '''
        Choose a possible future to expand. Grow the tree if it is appropriate.

        To implement the functionality in this correctly, update:
        - _widen(): determine if we should add an action to this node
        - _score(): rank children in the order you want to explore them
        - _rollout(): called by rollout(). simulate play forward in time, or
                    otherwise predict the expected future value of a state.
        '''

        visited = []

        done = False
        steps = 0

        '''
        Main loop: continue until we reach the end of the tree or abort for one
        reason or another.
        '''
        while steps < max_depth:
            assert node.initialized

            steps += 1
            node.n_visits += 1

            length = len(node.children)
            final_reward = node.reward

            # Add this node's reward to the vector of visited states.
            visited.append((node, final_reward))

            # optionally expand internal nodes
            if node.terminal:
                break
            elif self._can_widen and \
                    (can_widen or (length == 0 and self._dfs)) \
                    and self._widen(node):
                # sample an action from this node that we haven't explored yet
                action = self.sample(node)
                if action:
                    # add this action as a new child
                    node.children.append(Node(action=action))
                    can_widen = False
                    length += 1

            if length is 0:
                break

            # This is a visited node, which means that it has children we can
            # consider. We want to score these children using our provided scoring
            # function and select the next one to expand upon.
            # -----------------------------------------------------------------------
            # Compute  scores
            score = [0] * length
            for i, child in enumerate(node.children):
                score[i] = self._score(node, child)

            # choose the child with the best score
            max_idx, max_score = max(
                enumerate(score), key=operator.itemgetter(1))

            # instantiate child and select it
            child = node.children[max_idx]
            if not child.initialized:
                # fork the world and apply the correct action
                node.instantiate(child)
                if self._initialize:
                    self._initialize(child)

            node = child

        acc_reward = 0
        for node, reward in reversed(visited):
            acc_reward += reward
            node.update(acc_reward, final_reward, steps)

    '''
  Instantiate the specified child by forking from the current parent.
  '''

    def instantiate(self, parent, child):
        if not child.initialized:
            # fork the world and apply the correct action
            parent.instantiate(child)
            if self._initialize:
                self._initialize(child)

    '''
  Initialize the specified node.
  '''

    def initialize(self, node):
        if self._initialize:
            self._initialize(node)

    '''
  Descend through the tree until we reach the next node we want to expland.

  Procedure for learning:
  # take action
  action.apply(node)
  policies.select(node, can_widen=False)

  # if not done...
  # get next node to expand
  node = policies.getNext(self, root)
  features = node.features()
  return zero reward, features

  # if done...
  extract() and return reward associated with the best path
  '''

    def getNext(self, node, max_depth=10):

        if not self_widen:
            raise RuntimeError(
                'For now, getNext() only supports widening trees.')

        if max_depth == 0 or node.terminal:
            return None
        elif self._widen(node):
            return node
        elif len(node.children) == 0:
            return node
        else:
            length = len(node.children)
            score = [0] * length
            for i, child in zip(xrange(length), node.children):
                score[i] = self._score(node, child)
            max_idx, max_score = max(
                enumerate(score), key=operator.itemgetter(1))
            return self.getNext(node.children[max_idx])

    '''
  Explore the tree down from the root.
  '''

    def explore(self, node):
        self.select(node, self.max_depth, True)

    '''
  Just call the _extract() function we provided
  '''

    def extract(self, root):
        return self._extract(root)

'''
A generic MCTS action takes a node and produces another node.
'''


class AbstractMctsAction(AbstractAction):

    def apply(self, node):
        pass

    def update(self, node):
        pass

    def getAction(self, node):
        pass

'''
Abstract class that generates the "next" action from a particular state.

Unlike many of these, the abstract sampler actually has a few associated actions.

Inputs:
  - parent node

Outputs:
  - new action to take from this node
'''


class AbstractSample(object):

    def __call__(self, node):
        action = self._sample(node)
        if not action is None and not isinstance(action, AbstractMctsAction):
            raise RuntimeError(
                'for this to work, sampler must generate an MCTS abstact action.')
        return action

    def _sample(self, node):
        raise NotImplementedError('sampler._sample() not implemented!')

    def update(self, action, r):
        '''
        This function is provided as a way of updating an expected value function
        in the case where we have a continuous function.
        '''
        pass

    '''
  Implementing this function should return an entry from the whole list of
  MCTS actions that this sampler might generate from a particular state. It's
  not necessary to implement for most problems.
  '''

    def getOption(self, node, idx):
        raise NotImplementedError('sampler.getOption() not implemented!')

    '''
  Return the number of options possible from this node. It should be a constant number.
  '''

    def numOptions(self):
        raise NotImplementedError('sampler.numOptions() not implemented!')

    '''
  Returns a set of available options not dependent on the state.
  '''

    def getPolicies(self):
        raise NotImplementedError('sampler.getPolicies() not implemented!')


'''
This class computes a rollout from a particular MCTS node.

The most common way of doing this is just to do a simulation out to some
horizon. Another option that involves less compputation is to use a learned
value function and compute the expected value of a particular node/action pair
beyond this point.

Inputs:
  - node
  - depth of rollout

Outputs:
  - same as select(): data associated with a simulated play to the horizon

'''


class AbstractRollout(object):

    def __call__(self, node, depth):
        raise NotImplementedError('rollout.__call__() not implemented!')

'''
Take a node and construct the abstract representations of all of its children,
plus set their prior probabilities correctly.

Inputs:
  - parent node

Outputs:
  - none! parent's children should be created.
'''


class AbstractInitialize(object):
    ticks = 10

    def __call__(self, node):
        raise NotImplementedError('rollout.__call__() not implemented!')

'''
How valuable is this child?

Inputs:
  - parent node
  - child node

Outputs:
  - float score associated with child
'''


class AbstractScore(object):

    def __call__(self, parent, child):
        raise NotImplementedError('score.__call__() not implemented!')

'''
Widen the tree by adding a new entity.
This function says if we can widen: it returns a boolean.

Inputs:
  - parent node

Outputs:
  - boolean indicating if we should add a new child
'''


class AbstractWiden(object):

    def __call__(self, node):
        raise NotImplementedError('widen.__call__() not implemented!')

'''
Extract the best path through the tree.

Inputs:
  - root node

Outputs:
  - list of nodes
'''


class AbstractExtract(object):

    def __call__(self, node):
        raise NotImplementedError('extract.__call__() not implemented!')

'''
Run a whole search. May or may not use all of these different things we set up
above, passed in via the policies struct.

Inputs:
  - a root node
  - a set of policies for creating new nodes

Outputs:
  - elapsed time
  - a list of nodes
'''


class AbstractSearch(object):

    def __call__(self, node, policies, *args, **kwargs):
        raise NotImplementedError('extract.__call__() not implemented!')
