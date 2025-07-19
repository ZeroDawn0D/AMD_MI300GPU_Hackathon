from datetime import datetime, timezone
from src.classes import Event
from typing import List


class Interval:
    def __init__(self, low, high, attendees=None):
        self.low = low
        self.high = high
        self.attendees=attendees
    
    def update_time(self, low, high):
        self.low = low
        self.high = high

        
    @classmethod
    def from_event(cls, event: Event):
        interval = cls(
            low = get_unix_time(event.start_time),
            high = get_unix_time(event.end_time)
        )
        
        # Copy over remaining fields manually
        interval.creator = event.creator
        interval.start_time = event.start_time
        interval.end_time = event.end_time
        interval.summary = event.summary
        interval.window_start_time = event.window_start_time
        interval.window_end_time = event.window_end_time
        interval.final_start_time = event.final_start_time
        interval.final_end_time = event.final_end_time
        interval.attendees = event.attendees
        interval.priority = event.priority
        return interval
    
    def to_event(self) -> Event:
        start_time = datetime.fromtimestamp(self.low)
        end_time = datetime.fromtimestamp(self.high)
        creator = self.creator
        summary = self.summary

        event = Event(
            creator=creator,
            start_time=start_time,
            end_time=end_time,
            summary=summary,
            attendees=self.attendees
        )
        event.priority = self.priority
        return event

    def overlaps(self, other):
        time_overlap = self.low <= other.high and other.low <= self.high
        attendee_overlap = bool(set(self.attendees) & set(other.attendees))
        return time_overlap and attendee_overlap


RED = "RED"
BLACK = "BLACK"


class IntervalTreeNode:
    def __init__(self, interval: Interval, color=RED):
        self.interval = interval       # [low, high]
        self.max = interval.high       # max high in subtree
        self.left = None # Left child
        self.right = None # Right child
        self.parent = None
        self.color = color             # red or black



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
    
    def search_all(self,
                   interval: Interval,
                   node=None,
                   result=None) -> List[IntervalTreeNode]:
        if result is None:
            result = []
        if node is None:
            node = self.root
        if node == self.NIL:
            return result

        # Traverse left subtree only if potential overlaps exist
        if node.left != self.NIL and node.left.max >= interval.low:
            self.search_all(interval, node.left, result)

        # Check current node for overlap
        if node.interval.overlaps(interval):
            result.append(node)

        # Traverse right subtree if intervals could still overlap
        if node.right != self.NIL and node.interval.low <= interval.high:
            self.search_all(interval, node.right, result)

        return result


    def inorder(self, x=None, result=None) -> List[IntervalTreeNode]:
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
    
    def delete(self, interval):
        """
        Deletes a node with the given interval from the tree.
        """
        z = self._find_node(self.root, interval)
        if z == self.NIL:
            return  # Not found

        y = z
        y_original_color = y.color
        if z.left == self.NIL:
            x = z.right
            self._transplant(z, z.right)
        elif z.right == self.NIL:
            x = z.left
            self._transplant(z, z.left)
        else:
            y = self._minimum(z.right)
            y_original_color = y.color
            x = y.right
            if y.parent == z:
                x.parent = y
            else:
                self._transplant(y, y.right)
                y.right = z.right
                y.right.parent = y

            self._transplant(z, y)
            y.left = z.left
            y.left.parent = y
            y.color = z.color
            self._update_max(y)

        self._update_ancestors_max(x.parent)

        if y_original_color == BLACK:
            self._fix_delete(x)

    def _find_node(self, node, interval):
        while node != self.NIL:
            if (interval.low == node.interval.low 
                and interval.high == node.interval.high
                and set(interval.attendees) == set(node.interval.attendees)):
                return node
            elif interval.low < node.interval.low:
                node = node.left
            else:
                node = node.right
        return self.NIL

    def _minimum(self, node):
        while node.left != self.NIL:
            node = node.left
        return node

    def _transplant(self, u, v):
        if u.parent is None:
            self.root = v
        elif u == u.parent.left:
            u.parent.left = v
        else:
            u.parent.right = v
        v.parent = u.parent

    def _fix_delete(self, x):
        while x != self.root and x.color == BLACK:
            if x == x.parent.left:
                w = x.parent.right
                if w.color == RED:
                    w.color = BLACK
                    x.parent.color = RED
                    self.left_rotate(x.parent)
                    w = x.parent.right
                if w.left.color == BLACK and w.right.color == BLACK:
                    w.color = RED
                    x = x.parent
                else:
                    if w.right.color == BLACK:
                        w.left.color = BLACK
                        w.color = RED
                        self.right_rotate(w)
                        w = x.parent.right
                    w.color = x.parent.color
                    x.parent.color = BLACK
                    w.right.color = BLACK
                    self.left_rotate(x.parent)
                    x = self.root
            else:
                w = x.parent.left
                if w.color == RED:
                    w.color = BLACK
                    x.parent.color = RED
                    self.right_rotate(x.parent)
                    w = x.parent.left
                if w.right.color == BLACK and w.left.color == BLACK:
                    w.color = RED
                    x = x.parent
                else:
                    if w.left.color == BLACK:
                        w.right.color = BLACK
                        w.color = RED
                        self.left_rotate(w)
                        w = x.parent.left
                    w.color = x.parent.color
                    x.parent.color = BLACK
                    w.left.color = BLACK
                    self.right_rotate(x.parent)
                    x = self.root
        x.color = BLACK
    

def get_unix_time(time_val: datetime) -> int:
    return int(time_val.timestamp())
    

class IntervalTreeScheduler:
    def __init__(self, event_list: List[Event]):
        self.interval_list = [Interval.from_event(event) for event in event_list]
        self.interval_tree = self.create_interval_tree(event_list)

    def __str__(self):
        answer = "In order traversal of interval tree:\n"
        list_nodes = self.interval_tree.inorder()
        for node in list_nodes:
            answer+= f"[{datetime.fromtimestamp(node.interval.low)}, {datetime.fromtimestamp(node.interval.high)}], {node.interval.summary}, priority = {node.interval.priority} \n"
            answer+= f"attendees: {node.interval.attendees} \n"
            answer += '\n'
        return answer

    def create_interval_tree(self, event_list: List[Event]) -> IntervalTree:
        interval_tree = IntervalTree()
        for event in event_list:
            interval = Interval.from_event(event)
            interval_tree.insert(interval)
        return interval_tree
    
    def insert_event(self, event: Event):
        event_interval = Interval.from_event(event)
        clashing_interval_tree_nodes = self.interval_tree.search_all(event_interval)
        clashing_intervals = [x.interval for x in clashing_interval_tree_nodes]
        clashing_intervals.append(event_interval)
        sorted_clashing_intervals = sorted(clashing_intervals, 
                                           key = lambda x: x.priority,
                                           reverse=True)
        for interval in sorted_clashing_intervals:
            self.interval_tree.delete(interval)
            new_low, new_high = self.find_nearest_slot(interval)
            interval.update_time(new_low,new_high)
            self.interval_tree.insert(interval)
    
    def find_nearest_slot(self, interval, step=300, search_window=86400*7):
        # TODO: Add proper window limitations
        duration = interval.high - interval.low
        original_start = interval.low
        for offset in range(step, search_window + step, step):
            # Try moving earlier
            candidate_start_earlier = original_start - offset
            candidate_interval_earlier = Interval(candidate_start_earlier,
                                                  candidate_start_earlier + duration,
                                                  interval.attendees)
            if not self.interval_tree.search(candidate_interval_earlier):
                return candidate_start_earlier, candidate_start_earlier + duration

            # Try moving later
            candidate_start_later = original_start + offset
            candidate_interval_later = Interval(candidate_start_later,
                                                candidate_start_later + duration,
                                                interval.attendees)
            if not self.interval_tree.search(candidate_interval_later):
                return candidate_start_later, candidate_start_later + duration