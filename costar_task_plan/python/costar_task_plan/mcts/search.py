
import timeit

from abstract import AbstractSearch

'''
Search through the tree exhaustively.
'''
class DepthFirstSearch(AbstractSearch):

  def __call__(self, root, policies, max_expansions=10, *args, **kwargs):
    start_time = timeit.default_timer()
    policies.initialize(root)
    nodes_to_visit = [root]

    best_reward = -float('inf')
    best_node = None

    while len(nodes_to_visit) > 0:
      # Get the next node to visit.
      node = nodes_to_visit.pop()

      if node.terminal:
        if node.accumulatedReward() > best_reward:
          best_reward = node.accumulatedReward()
          best_node = node
      else:
        expanded = 0
        # add any possible children from the root
        for child in node.children:
          expanded += 1
          policies.instantiate(node, child)
          nodes_to_visit.append(child)

          if expanded > max_expansions:
            break

    path = []
    if best_node is not None:
      path.append(best_node)
      while best_node.parent is not None:
        best_node = best_node.parent

    path.reverse()

    elapsed = timeit.default_timer() - start_time
    return elapsed, path

'''
The "default" method for performing a search. Runs a certain number of
iterations according to the full set of policies provided.
'''
class MonteCarloTreeSearch(AbstractSearch):

  def __call__(self, root, policies, iter=100, *args, **kwargs):
    policies.initialize(root)
    start_time = timeit.default_timer()
    for i in xrange(iter):
        policies.explore(root)
    path = policies.extract(root)

    elapsed = timeit.default_timer() - start_time
    return elapsed, path
