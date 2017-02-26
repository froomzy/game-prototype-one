

class BoundingSpace:
    """An infinity wide space that contains colliders

    A bounding space is similar to a bounding box, except that it is not
    interested in the x axis. An object is in a bounding space if it's y
    coordinates wholely fall within the range the bounding space covers.

    When comparing bounding spaces they may be any of the following:
    * Not intersecting: The two spaces y axis do not overlap in any way
    * Intersecting: At least some part of one space lies within the other

    When two bounding spaces are intersecting they may be:
    * Overlapping: Part of one space lies within the other
    * Containing: One space exists entirely within the other
    * Equal: The two spaces represent the same area"""

    def __init__(self, bottom: float, top: float) -> None:
        self.bottom = bottom
        self.top = top

    def intersect(self, other: 'BoundingSpace') -> bool:
        if self.bottom < other.bottom > self.top:
            return True
        if self.bottom < other.top > self.top:
            return True
        return False

class Node:
    def __init__(self, ):
        self.colliders = []
        self.left_child = None
        self.rigth_child = None
        self.bounding_box = None


class CollisionTree:
    def __init__(self):
        self.root = None

    def add_collider(self, collider):
        pass

    def create_bounding_box(self, collider):
        pass
