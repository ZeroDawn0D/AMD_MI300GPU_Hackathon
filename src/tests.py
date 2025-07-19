from scheduling.interval_tree import *
def test_insert_and_search():
    tree = IntervalTree()
    intervals = [
        (15, 20),
        (10, 30),
        (17, 19),
        (5, 20),
        (12, 15),
        (30, 40)
    ]
    for low, high in intervals:
        tree.insert(Interval(low, high))
    
    # Overlapping case
    assert tree.search(Interval(14, 16)) is not None  # overlaps with [12,15] or [10,30]

    # Non-overlapping case
    assert tree.search(Interval(40, 50)) is not None  # overlaps with [30,40]

    # No match
    assert tree.search(Interval(100, 110)) is None

def test_edge_overlaps():
    tree = IntervalTree()
    tree.insert(Interval(10, 20))
    
    # Touching at boundaries — should be considered overlapping
    assert tree.search(Interval(20, 25)) is not None
    assert tree.search(Interval(5, 10)) is not None

    # Outside boundaries
    assert tree.search(Interval(21, 25)) is None
    assert tree.search(Interval(0, 9)) is None

def test_inorder_structure():
    tree = IntervalTree()
    intervals = [(20, 30), (10, 15), (25, 35), (5, 8)]
    for low, high in intervals:
        tree.insert(Interval(low, high))
    
    # Check in-order traversal produces intervals in sorted order of `low`
    inorder_nodes = tree.inorder()
    lows = [node.interval.low for node in inorder_nodes]
    assert lows == sorted(lows)

def test_max_field_propagation():
    tree = IntervalTree()
    tree.insert(Interval(10, 15))
    tree.insert(Interval(5, 8))
    tree.insert(Interval(12, 20))

    # Find the node with low=10
    nodes = tree.inorder()
    for node in nodes:
        if node.interval.low == 10:
            assert node.max == 20
            break
    else:
        raise AssertionError("Expected node with interval [10, 15] not found")

if __name__ == "__main__":
    test_insert_and_search()
    test_edge_overlaps()
    test_inorder_structure()
    test_max_field_propagation()
    print("All tests passed.")