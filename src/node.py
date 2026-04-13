from random import randint, random
OPERATORS = ['+', '-', '*', '/']
POW_MIN_EXP = 2
POW_MAX_EXP = 5
CONST_MIN = -10
CONST_MAX = 10
CONST_PROB = 0.6
X_PROB = 0.25


# Recursively traverse the tree and print values.
def display_in_order(current_node):
    # If we have reached a leaf, return.
    if current_node is None:
        return
    # Print left subtree.
    display_in_order(current_node.left)
    print(current_node.value)
    display_in_order(current_node.right)
    return


class Node:
    # `op` nodes are operators, `num` nodes are terminal values.
    def __init__(self, node_type, depth):
        self.value = 0
        self.node_type = node_type
        self.right = None
        self.left = None
        self.depth = depth

        if node_type == 'op':
            self.value = OPERATORS[randint(0, 3)]
        elif node_type == 'num':
            # For `num` leaves, keep 3 terminal forms:
            # constant, variable x, or monomial x**a.
            # The monomial x**a is intentionally kept to guide the search
            # toward polynomial expressions and reduce search difficulty.
            r = random()
            if r < CONST_PROB:
                self.value = randint(CONST_MIN, CONST_MAX)
            elif r < CONST_PROB + X_PROB:
                self.value = 'x'
            else:
                self.value = f"x**{randint(POW_MIN_EXP, POW_MAX_EXP)}"
        else:
            raise ValueError('error, must be op or num')




    # Changes the value of a node to a random operator.
    def change_to_operator(self):
        self.node_type = 'op'
        self.value = OPERATORS[randint(0, 3)]

        # Avoid divide-by-zero when the right child is already known.
        if (
            self.value == '/'
            and self.right is not None
            and self.right.node_type == 'num'
            and self.right.value == 0
        ):
            self.value = OPERATORS[randint(0, 2)]


    # Takes a numeric node, turns it into an operator,
    # and gives it two numeric children.
    def add_children(self):
        if self.left is None and self.right is None:
            self.change_to_operator()
            self.left = Node('num', self.depth + 1)
            self.right = Node('num', self.depth + 1)

            # Avoid creating explicit division by zero in a new subtree.
            while self.value == '/' and self.right.value == 0:
                self.value = OPERATORS[randint(0, 2)]

            # We have added two children to the shallowest node.
            return
        else:
            raise ValueError('error, to add children the node must have none')
                

    # Borrowed method to print the tree.
    # https://stackoverflow.com/questions/34012886/print-binary-tree-level-by-level-in-python
    def display(self):
        lines, _, _, _ = self._display_aux()
        for line in lines:
            print(line)

    def _display_aux(self):
        """Returns list of strings, width, height, and horizontal coordinate of the root."""
        # No child.
        if self.right is None and self.left is None:
            line = '%s' % self.value
            width = len(line)
            height = 1
            middle = width // 2
            return [line], width, height, middle

        # Only left child.
        if self.right is None:
            lines, n, p, x = self.left._display_aux()
            s = '%s' % self.value
            u = len(s)
            first_line = (x + 1) * ' ' + (n - x - 1) * '_' + s
            second_line = x * ' ' + '/' + (n - x - 1 + u) * ' '
            shifted_lines = [line + u * ' ' for line in lines]
            return [first_line, second_line] + shifted_lines, n + u, p + 2, n + u // 2

        # Only right child.
        if self.left is None:
            lines, n, p, x = self.right._display_aux()
            s = '%s' % self.value
            u = len(s)
            first_line = s + x * '_' + (n - x) * ' '
            second_line = (u + x) * ' ' + '\\' + (n - x - 1) * ' '
            shifted_lines = [u * ' ' + line for line in lines]
            return [first_line, second_line] + shifted_lines, n + u, p + 2, u // 2

        # Two children.
        left, n, p, x = self.left._display_aux()
        right, m, q, y = self.right._display_aux()
        s = '%s' % self.value
        u = len(s)
        first_line = (x + 1) * ' ' + (n - x - 1) * '_' + s + y * '_' + (m - y) * ' '
        second_line = x * ' ' + '/' + (n - x - 1 + u + y) * ' ' + '\\' + (m - y - 1) * ' '
        if p < q:
            left += [n * ' '] * (q - p)
        elif q < p:
            right += [m * ' '] * (p - q)
        zipped_lines = zip(left, right)
        lines = [first_line, second_line] + [a + u * ' ' + b for a, b in zipped_lines]
        return lines, n + m + u, max(p, q) + 2, n + u // 2
