from datetime import datetime, timezone
from src.classes import Event

class Interval:
    def __init__(self, low, high):
        self.low = low
        self.high = high

    def overlaps(self, other):
        return self.low <= other.high and other.low <= self.high
    
RED = "RED"
BLACK = "BLACK"


class IntervalTreeNode:
    def __init__(self, interval, color=RED):
        self.interval = interval       # [low, high]
        self.max = interval.high       # max high in subtree
        self.left = None # Left child
        self.right = None # Right child
        self.parent = None
        self.color = color             # red or black

def interval_search(root: IntervalTreeNode, 
                    query: IntervalTreeNode):
    
    x = root
    while x is not None and not do_overlap(x.interval, query):
        if x.left is not None and x.left.max >= query.low:
            x = x.left
        else:
            x = x.right
    return x

# Two intervals [a1, a2] and [b1, b2] overlap when
# a1 <= b2 and b1 <= a2
def do_overlap(i1: Interval,
               i2: Interval)->bool:
    return i1.low < i2.high and i2.low <= i1.high

class IntervalTree:
    def __init__(self):
        self.NIL =IntervalTreeNode(Interval(0, 0), color=BLACK)
        self.NIL.max = float('-inf')
        self.root = self.NIL


    def left_rotate(self,x):
        y = x.right
        x.right = y.left
        if y.left != self.NIL:
            y.left.parent = x
        y.parent = x.parent

        # Link y to x's parent
        if x.parent is None:
            self.root = y
        elif x == x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y

        y.left = x
        x.parent = y

        # Update max values after rotation
        self._update_max(x)
        self._update_max(y)
    
    def right_rotate(self,x):
        y = x.left
        x.left = y.right
        if y.right != self.NIL:
            y.right.parent = x
        y.parent = x.parent

        # Link y to x's parent
        if x.parent is None:
            self.root = y
        elif x == x.parent.right:
            x.parent.right = y
        else:
            x.parent.left = y

        y.right = x
        x.parent = y

        # Update max values after rotation
        self._update_max(x)
        self._update_max(y)
    
    def insert(self, interval):
        node = IntervalTreeNode(interval)
        node.left = node.right = self.NIL
        y = None
        x = self.root
        while x != self.NIL:
            y = x
            if node.interval.low < x.interval.low:
                x = x.left
            else:
                x = x.right

        node.parent = y
        if y is None:
            self.root = node
        elif node.interval.low < y.interval.low:
            y.left = node
        else:
            y.right = node

        node.color = RED
        self._fix_insert(node)
    
    def _fix_insert(self, z):
        """
        Fixes red-black tree properties after insertion.
        """
        while z.parent and z.parent.color == RED:
            if z.parent == z.parent.parent.left:
                y = z.parent.parent.right  # Uncle
                if y and y.color == RED:
                    # Case 1: Uncle is red
                    z.parent.color = BLACK
                    y.color = BLACK
                    z.parent.parent.color = RED
                    z = z.parent.parent
                else:
                    if z == z.parent.right:
                        # Case 2: z is right child
                        z = z.parent
                        self.left_rotate(z)
                    # Case 3: z is left child
                    z.parent.color = BLACK
                    z.parent.parent.color = RED
                    self.right_rotate(z.parent.parent)
            else:
                # Symmetric cases for z's parent on the right
                y = z.parent.parent.left
                if y and y.color == RED:
                    z.parent.color = BLACK
                    y.color = BLACK
                    z.parent.parent.color = RED
                    z = z.parent.parent
                else:
                    if z == z.parent.left:
                        z = z.parent
                        self.right_rotate(z)
                    z.parent.color = BLACK
                    z.parent.parent.color = RED
                    self.left_rotate(z.parent.parent)

        self.root.color = BLACK
        self._update_ancestors_max(z)

    def _update_ancestors_max(self, x):
        """
        Updates max values from x up to the root.
        """
        while x:
            self._update_max(x)
            x = x.parent

    def _update_max(self, x):
        """
        Updates the max value for node x.
        """
        if x == self.NIL:
            return
        x.max = max(
            x.interval.high,
            x.left.max if x.left else float('-inf'),
            x.right.max if x.right else float('-inf')
        )
 
    def search(self, interval):
        """
        Searches for a single interval that overlaps with the given one.
        Returns the node if found, otherwise None.
        """
        x = self.root
        while x != self.NIL and not x.interval.overlaps(interval):
            if x.left != self.NIL and x.left.max >= interval.low:
                x = x.left
            else:
                x = x.right
        return x if x != self.NIL else None

    def inorder(self, x=None, result=None):
        """
        Returns in-order traversal of tree (for debugging/inspection).
        """
        if result is None:
            result = []
        if x is None:
            x = self.root
        if x != self.NIL:
            self.inorder(x.left, result)
            result.append(x)
            self.inorder(x.right, result)
        return result
    


class IntervalTreeScheduler:
    def __init__(self, event_list):
        self.interval_tree = self.create_interval_tree(event_list)


    def create_interval_tree(event_list):
        ...