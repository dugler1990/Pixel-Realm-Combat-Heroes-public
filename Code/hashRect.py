class HashableRect:
    def __init__(self,
                 rect,
                 _id = -1,
                 direction = None,
                 sprite_type = None,
                 mask = None):
        self._id = _id
        self.rect = rect
        self.mask = mask
        self.direction = direction 
        self.sprite_type = sprite_type
        self.left = rect.left
        self.right = rect.right
        self.bottom = rect.bottom
        self.top = rect.top
    def __hash__(self):
        return hash((self.rect.left, self.rect.top, self.rect.width, self.rect.height))

    def __eq__(self, other):
        return (
            isinstance(other, HashableRect) and
            self.rect == other.rect and 
            self.direction == other.direction and
            self.sprite_type == other.sprite_type
        )