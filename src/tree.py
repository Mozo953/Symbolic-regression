from node import *
from random import *
from readData import *
import math
import copy
MUTATE_PROB = 0.7
#SIZE_PENALTY_COEFF = 0.1
FITNESS_INVALID_PENALTY = 1e6
DIV_ZERO_EPS = 1e-12
LAMBDA_SIZE = 1e-5  # Adjustable coefficient to penalize complexity.
MAX_TREE_DEPTH = 10  # Recommended maximum depth (6 to 8).
# To do later: add other variables.




class Tree:
    # Adjust later to avoid all trees having exactly the same depth.
    def __init__(self, max_depth=1, mode='full'):
        # Tree construction only uses max depth in full/grow mode.
        target_depth = max(1, int(max_depth))
        mode = str(mode).lower()
        if mode not in ('full', 'grow'):
            raise ValueError('error, mode must be full or grow')

        self.fitness = float('inf')
        self.root = self._generate_node(1, target_depth, mode)
        self.depth = self.update_depth(self.root)
        self.size = self.update_size(self.root)

    def _generate_node(self, depth, max_depth, mode):
        # Maximum depth reached: numeric leaf required.
        if depth >= max_depth:
            return Node('num', depth)

        # Full mode: all internal nodes are operators.
        if mode == 'full':
            node = Node('op', depth)
            node.left = self._generate_node(depth + 1, max_depth, mode)
            node.right = self._generate_node(depth + 1, max_depth, mode)
            return node

        # Grow mode: we may stop earlier, except at the root.
        if depth > 1 and random() < 0.5:   # WARNING, this could be a hyperparameter to tune.
            return Node('num', depth)

        node = Node('op', depth)
        node.left = self._generate_node(depth + 1, max_depth, mode)
        node.right = self._generate_node(depth + 1, max_depth, mode)
        return node

    def _list_nodes(self, include_root=True):
        if self.root is None:
            return []

        nodes = []
        stack = [(self.root, None, '', 1)]
        while stack:
            node, parent, direction, depth = stack.pop()
            if include_root or parent is not None:
                nodes.append((node, parent, direction, depth))
            if node.right is not None:
                stack.append((node.right, node, 'r', depth + 1))
            if node.left is not None:
                stack.append((node.left, node, 'l', depth + 1))
        return nodes

    def _update_node_depths(self, node, depth=1):
        if node is None:
            return
        node.depth = depth
        self._update_node_depths(node.left, depth + 1)
        self._update_node_depths(node.right, depth + 1)

    def _update_metadata(self):
        self._update_node_depths(self.root)
        self.depth = self.update_depth(self.root)
        self.size = self.update_size(self.root)
        self.fitness = float('inf')

    # To compare trees: equal only if it is the same reference.
    def __eq__(self, other):
        if self is other:
            return True
        else:
            return False

    # For ordering: smaller = better fitness.
    def __lt__(self, other):
        if self.fitness < other.fitness:
            return True
        else:
            return False




###########################FITNESS#########################
    # Returns the tree value for an input x.
    def evaluate(self, x):
        return self.evaluate_tree(self.root, x)


    # Building block 1: compute our f(x).
    def evaluate_tree(self, node, x):
        # Empty tree.
        if node is None:
            return 0

        # Leaf node.
        if node.left is None and node.right is None:
            if node.value=='x':
                return float(x)
            if isinstance(node.value, str) and node.value.startswith('x**'):
                try:
                    exp = int(node.value.split('**', 1)[1])
                except (IndexError, ValueError):
                    return None
                return float(x) ** exp
            if isinstance(node.value, (int, float)):
                return float(node.value)
            return None

        # Evaluate the left subtree.
        left_sum = self.evaluate_tree(node.left, x)

        # Evaluate the right subtree.
        right_sum = self.evaluate_tree(node.right, x)
        if left_sum == None or right_sum == None:
            return None

        # Apply the node operation.
        if node.value == '+':
            return float(left_sum + right_sum)

        elif node.value == '-':
            return float(left_sum - right_sum)

        elif node.value == '*':
            return float(left_sum * right_sum)

        elif node.value == '/':
            # TODO: later replace with a proper GP protected division
            # (with configurable threshold/regularization) for more stability.
            if abs(right_sum) > DIV_ZERO_EPS:
                return float(left_sum / right_sum)
            return float('inf')

        return None


    # Compute the tree size for penalization.
    def tree_size(self, node):
        if node is None:
            return 0
        return 1 + self.tree_size(node.left) + self.tree_size(node.right)

    # Compute the tree fitness with the penalty term.
    def compute_fitness(self, data):
        if not data:
            self.fitness = float('inf')
            return self.fitness

        # Mean squared error over all points.
        sqrerr = 0.0
        invalid_count = 0
        for x, y in data:
            try:
                ans = self.evaluate(x)
                if ans is None:
                    invalid_count += 1
                    continue
                ans_val = float(ans)
            except Exception:
                invalid_count += 1
                continue

            if not math.isfinite(ans_val):
                invalid_count += 1
                continue

            sqrerr += (ans_val - y) ** 2

        # No evaluable point: invalid individual.
        if invalid_count == len(data):
            self.fitness = float('inf')
            return self.fitness

        # Avoid an artificially low fitness if some points are invalid.
        if invalid_count:
            sqrerr += FITNESS_INVALID_PENALTY * invalid_count

        mse = sqrerr / len(data)
        size = self.tree_size(self.root)
        fitness = mse + LAMBDA_SIZE * size    # Penalty term. TODO: expose lambda as a parameter.
        self.fitness = fitness
        return fitness








###########################CROSSOVER#########################



    # Cross two trees.
    def crossover(self, other):
        # Non-destructive crossover: work on deep copies.
        child = copy.deepcopy(self)
        donor = copy.deepcopy(other)

        targets = child._list_nodes(include_root=True)
        donors = donor._list_nodes(include_root=True)
        if not targets or not donors:
            return child

        _, parent1, direct1, _ = choice(targets)
        root2, _, _, _ = choice(donors)

        graft = copy.deepcopy(root2)
        if parent1 is None:
            child.root = graft
        elif direct1 == 'l':
            parent1.left = graft
        elif direct1 == 'r':
            parent1.right = graft

        child._update_metadata()
        return child


#############################################################""

    # def getRootLength(self,root,root_length):
    #     print self.depth
    #     self.root.display()
    #     if root==None:
    #         return root_length
    #     return(max(self.getRootLength(root.left,root_length+1),
    #     self.getRootLength(root.right,root_length+1)))

    # Recursive algorithm that returns the depth of the tree.
    def update_depth(self, root, depth=0):
        if root == None:
            return depth
        depth += 1
        return max(self.update_depth(root.right, depth),
        self.update_depth(root.left, depth))

    # Recursive algorithm that updates the tree size.
    def update_size(self, root, size=0):
        if root == None:
            return 0
        return 1 + self.update_size(root.right, size) + self.update_size(root.left, size)





#############################MUTATION#####################################################
    # Mutate the tree by uniformly replacing an existing subtree.
    def mutate(self, root=None):
        if root is None:
            root = self.root
        if root is None:
            return

        current_depth = self.update_depth(root)
        candidates = self._list_nodes(include_root=True)
        if not candidates:
            return

        _, parent, direct, node_depth = choice(candidates)

        # Generate a new random subtree (grow mode).
        lower_bound = node_depth + 1
        if lower_bound > MAX_TREE_DEPTH:
            return

        upper_bound = min(MAX_TREE_DEPTH, max(lower_bound, current_depth + 2))
        new_max_depth = randint(lower_bound, upper_bound)
        new_subtree = self._generate_node(node_depth, new_max_depth, 'grow')

        if parent is None:
            self.root = new_subtree
        elif direct == 'l':
            parent.left = new_subtree
        else:
            parent.right = new_subtree

        self._update_metadata()
