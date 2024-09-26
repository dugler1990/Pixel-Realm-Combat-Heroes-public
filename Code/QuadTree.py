from pygame import Rect

class QuadTreeManager:
    def __init__(self):
        self.item_mapping = {}

    def add_mapping(self, item_id, node, index):
        #print(self.item_mapping)
        self.item_mapping[item_id] = (node, index)

    def remove_mapping(self, item_id):
        del self.item_mapping[item_id]

    def get_mapping(self, item_id):
        return self.item_mapping.get(item_id, (None, None))
    #@profile
    def remove(self, item_id,remove_existing=True):## dont we always remove existing here , bit confusing.
        node, index = self.get_mapping(item_id)
       #print(f"item mapping : {self.item_mapping}")
        
        if node is not None and index is not None:
            #if item_id ==1:
               #print('in theory deleting item 1:')
               #print(f"node : {node}  index : {index}")
            
            
            #del node.items[index]
            if remove_existing:
                node.remove(index)
                #print(f"removed index :{index}")
            node_found = False
            # Adjust indices in the mappings for items in the same node
            for mapping_index, item_mapping in self.item_mapping.items():
                #print(f"mapping index  : {mapping_index}, {item_id}")
                #print(f"item mapping : {item_mapping} node  : {node} ")
                if item_mapping[0] is node: # and node_found==False:
                    node_found = True
                    
                    
                    # ok, so im considering doing this node found or not optimization
                    
                    # but it seems to be going over every single mapping in the item_mapping as if there is a single item mapping
                    
                    # for the entire quad tree, if there is just an item mapping per node, once i have found the node, i do not need to keep on checking:
                        
                    # the way this is setup though, it seems, we are checking to see if the specific item is in the node we just changed and then we adapt its
                    
                    # index inside. hmm, this is inefficient, there is a reason to use the global map though, gpt is saying to use a mapping inside each node
                    
                    # inside each node is just a list though, the mapping is specifically to quickly delete from any node, the problem is that to keep this
                    
                    # updated, i need to adjust the indeces of the remaining node items. Maybe if as opposed to a hashmap(dict) i use some other data structure,
                    
                    # it should be easy enough to gather all of the mapping corresponding to a particular node as opposed to iterating over all of them.
                    
                    # # -> look at how this item mapping is created in the first place.
                    
                    # the mapping is used to imediately go to the right node and position for deletion, great,
                    
                    # issue is, i go through the entire map just to find the the entries which are in that node to readjust them after deletion,
                    
                    # what i have at the moment is, for deletion, the exact id of the entity in question and boom , node and position, 
                    
                    
                    
                    
                   #print("node match")
                    if mapping_index != item_id:
                    
                        if item_mapping[1] > index:
                            self.item_mapping[mapping_index] = (item_mapping[0], item_mapping[1] - 1)
            self.remove_mapping(item_id) # was hoping to not have to do t his and just overwrite but i cant get it worknig.

    def update_item_mask(self, item_id, mask):
        node, index = self.get_mapping(item_id)
        if node is not None and index is not None:
            node.update_item_mask(index,mask)


#self.manager = QuadTreeManager()
class QuadTree(object):
    """An implementation of a quad-tree.
 
    This QuadTree started life as a version of [1] but found a life of its own
    when I realised it wasn't doing what I needed. It is intended for static
    geometry, ie, items such as the landscape that don't move.
 
    This implementation inserts items at the current level if they overlap all
    4 sub-quadrants, otherwise it inserts them recursively into the one or two
    sub-quadrants that they overlap.
 
    Items being stored in the tree must be a pygame.Rect or have have a
    .rect (pygame.Rect) attribute that is a pygame.Rect
	    ...and they must be hashable.
    
    Acknowledgements:
    [1] http://mu.arete.cc/pcr/syntax/quadtree/1/quadtree.py
    """

    def __init__(self, items, depth=8, bounding_rect=None,manager=None):
        """Creates a quad-tree.
 
        @param items:
            A sequence of items to store in the quad-tree. Note that these
            items must be a pygame.Rect or have a .rect attribute.
            
        @param depth:
            The maximum recursion depth.
            
        @param bounding_rect:
            The bounding rectangle of all of the items in the quad-tree. For
            internal use only.
        """
        self.manager = manager
        self.num_items = 0
        #print("STARTING THE QUAD TREE !! ! ! ! ! ! ")
        # The sub-quadrants are empty to start with.
        self.nw = self.ne = self.se = self.sw = None
        #print(depth)
        #print(bounding_rect)
        #print(items)
        # If we've reached the maximum depth then insert all items into this
        self.item_mapping = {}
        # quadrant.
        self.depth = depth
        depth -= 1
        
        
        
        
        if bounding_rect:
            bounding_rect = Rect( bounding_rect )
            #print(bounding_rect)
            
        else:
            # If there isn't a bounding rect, then calculate it from the items.
            bounding_rect = Rect( items[0] )
            for item in items[1:]:
                bounding_rect.union_ip( item )
        self.bounding_rect = bounding_rect
        #print("MADE IT TO THIS PART OF THE QUAD TREEEE YAAAY")
        #print(f"depth:{depth}")
        cx = self.cx = bounding_rect.centerx
        cy = self.cy = bounding_rect.centery
        
        if depth == 0  or not items:
            self.items = items
            return
        #print("MADE IT TO THIS PART OF THE QUAD TREEEE YAAAY")
        # Find this quadrant's centre.

        #print(f" JUST DEFINED THE CX OF MAIN QUADTREE : {self.cx}")
        
        #print(self.cx, self.cy)

        self.items = []
        nw_items = []
        ne_items = []
        se_items = []
        sw_items = []

        for item in items:
            # Which of the sub-quadrants does the item overlap?
        
            in_nw = item.left <= cx and item.top <= cy
            in_sw = item.left <= cx and item.bottom >= cy
            in_ne = item.right >= cx and item.top <= cy
            in_se = item.right >= cx and item.bottom >= cy
                
            # If it overlaps all 4 quadrants then insert it at the current
            # depth, otherwise append it to a list to be inserted under every
            # quadrant that it overlaps.
            if in_nw and in_ne and in_se and in_sw:
                self.items.append(item)
            else:
                if in_nw: nw_items.append(item)
                if in_ne: ne_items.append(item)
                if in_se: se_items.append(item)
                if in_sw: sw_items.append(item)
            
        # Create the sub-quadrants, recursively.
        if nw_items:
            self.nw = QuadTree(nw_items, depth, (bounding_rect.left, bounding_rect.top, cx, cy), manager = self.manager)
        if ne_items:
            self.ne = QuadTree(ne_items, depth, (cx, bounding_rect.top, bounding_rect.right, cy), manager = self.manager)
        if se_items:
            self.se = QuadTree(se_items, depth, (cx, cy, bounding_rect.right, bounding_rect.bottom), manager = self.manager)
        if sw_items:
            self.sw = QuadTree(sw_items, depth, (bounding_rect.left, cy, cx, bounding_rect.bottom), manager = self.manager)
 
    
    def print_all(self):
       """Recursively prints all items and nested items in the quadtree."""
       print(f"Items in current node: {self.items}")
   
       if self.nw:
           print("Northwest sub-quadrant:")
           self.nw.print_all()
       if self.ne:
           print("Northeast sub-quadrant:")
           self.ne.print_all()
       if self.se:
           print("Southeast sub-quadrant:")
           self.se.print_all()
       if self.sw:
           print("Southwest sub-quadrant:")
           self.sw.print_all()
    
    #@profile
    def hit(self, rect):
        """Returns the items that overlap a bounding rectangle.
 
        Returns the set of all items in the quad-tree that overlap with a
        bounding rectangle.
        
        @param rect:
            The bounding rectangle being tested against the quad-tree. This
            must possess left, top, right and bottom attributes.
        """
    
        # Initialize an empty set for hits
        hits = set()
    
        # If there are items in the quad-tree
        if self.items:
            # Collect items that overlap with the rectangle
            hits.update(item for item in self.items if item.rect.colliderect(rect) and item._id != rect._id)


        # Recursively check the lower quadrants.
        if self.nw and rect.left <= self.cx and rect.top <= self.cy:
            hits |= self.nw.hit(rect)
        if self.sw and rect.left <= self.cx and rect.bottom >= self.cy:
            hits |= self.sw.hit(rect)
        if self.ne and rect.right >= self.cx and rect.top <= self.cy:
            hits |= self.ne.hit(rect)
        if self.se and rect.right >= self.cx and rect.bottom >= self.cy:
            hits |= self.se.hit(rect)
            
            
        return hits
    
    
            
    #@profile
    def insert(self, item, alive, remove_existing=True):
        """Inserts an item into the quad-tree.
    
        @param item:
            The item to insert into the quad-tree. The item must possess
            left, top, right, and bottom attributes.
        """
        # If the item is already in the quad-tree, return.
        if item in self.items:
            
            return
        
        if remove_existing:
            self.manager.remove(item._id)
        
        if alive:
            # If the current depth is 1, insert the item at this level.
            if self.depth == 1:
                #if item._id ==1:
                   #print(f'in theory inserting item 1:')
                   #print(f"node : {self}  index : {self.num_items}")
                
                self.items.append(item)
                self.manager.add_mapping(item._id, self, self.num_items)  # Store node and index
                #print(f"inserted index : {self.num_items}") 
                self.num_items += 1
                return
        
            # Check if the item belongs to any of the sub-quadrants.
            in_nw = item.left <= self.cx and item.top <= self.cy
            in_sw = item.left <= self.cx and item.bottom >= self.cy
            in_ne = item.right >= self.cx and item.top <= self.cy
            in_se = item.right >= self.cx and item.bottom >= self.cy
        
            # If the item overlaps all four quadrants, insert it at the current level.
            if in_nw and in_ne and in_se and in_sw:
                #if item._id ==1:
                   #print(f'in theory inserting item 1:')
                   #print(f"node : {self}  index : {self.num_items}")
                
                self.items.append(item)
                self.manager.add_mapping(item._id, self, self.num_items)  # Store node and index
                self.num_items += 1
                #print(f"inserted index : {self.num_items}")
                return
        
            # Otherwise, create sub-quadrants if they don't exist and recursively insert the item into them.
            if not self.nw:
                self.nw = QuadTree([],depth=self.depth - 1, bounding_rect=(self.bounding_rect.left, self.bounding_rect.top, self.cx, self.cy), manager=self.manager)
            if not self.ne:
                self.ne = QuadTree([],depth=self.depth - 1, bounding_rect=(self.cx, self.bounding_rect.top, self.bounding_rect.right, self.cy), manager=self.manager)
            if not self.se:
                self.se = QuadTree([],depth=self.depth - 1, bounding_rect=(self.cx, self.cy, self.bounding_rect.right, self.bounding_rect.bottom), manager=self.manager)
            if not self.sw:
                self.sw = QuadTree([],depth=self.depth - 1, bounding_rect=(self.bounding_rect.left, self.cy, self.cx, self.bounding_rect.bottom), manager=self.manager)
        
            # Recursively insert the item into the appropriate sub-quadrants.
            if in_nw:
                self.nw.insert(item, alive = alive)
            if in_ne:
                self.ne.insert(item, alive = alive)
            if in_sw:
                self.sw.insert(item, alive = alive)
            if in_se:
                self.se.insert(item, alive = alive)
    
    def remove(self,index):
        #print(self.items)
        #print(index)
        
        self.items.pop(index)
        self.num_items -= 1
        
    def update_item_mask(self,index,mask):
        self.items[index].mask = mask
        
    
    ##@profile
    # def remove_old(self, item_id):
    #     """Removes an item from the quad-tree by ID."""
    #     # Use a generator expression to find the first occurrence of the item with the specified ID
    #     item_to_remove = next((item for item in self.items if item._id == item_id), None)
    #     if item_to_remove:
    #         # Remove the item from the items list
    #         self.items.remove(item_to_remove)
    #         return True
        
    #     # Recursively remove item from sub-quadrants if present
    #     if self.nw:
    #         if self.nw.remove(item_id):
    #             return True
    #     if self.ne:
    #         if self.ne.remove(item_id):
    #             return True
    #     if self.se:
    #         if self.se.remove(item_id):
    #             return True
    #     if self.sw:
    #         if self.sw.remove(item_id):
    #             return True
        
    #     return False
            
            
            
            
            
         
    #     # Check if the item belongs to any of the sub-quadrants.
    #     in_nw = item.left <= self.cx and item.top <= self.cy
    #     in_sw = item.left <= self.cx and item.bottom >= self.cy
    #     in_ne = item.right >= self.cx and item.top <= self.cy
    #     in_se = item.right >= self.cx and item.bottom >= self.cy
    #     # If the item overlaps all four quadrants, insert it at the current level.
    #     if (in_nw and in_ne and in_se and in_sw) :
    #         self.items.append(item)
    #         self.manager.add_mapping( item._id ,self, self.num_items)  # Store node and index
    #         self.num_items += 1
            
            
    #        #print("INSERT on overlap")
    #        #print(f"INSERT node : {self}")
    #        #print(f"INSERT id : {item._id}")
    #        #print(f"INSERT num items state : {self.num_items}")
    #        #print(f"INSERT Item mapping state  : {self.manager.item_mapping}")
            
            
    #         return
        
    #     else:
    #         #print("Not matched")
    #         # Otherwise, insert it into the appropriate sub-quadrants.
    #         if in_nw:
    #             if not self.nw:
    #                 #Sprint("Not existing child 1")
    #                 self.nw = QuadTree([], 
    #                                    depth=self.depth - 1,
    #                                    bounding_rect=(self.bounding_rect.left, 
    #                                                   self.bounding_rect.top, 
    #                                                   self.cx,
    #                                                   self.cy),
    #                                    manager = self.manager)
    #             self.nw.insert(item)
    #         if in_ne:
    #             if not self.ne:
    #                 #print("Not existing child 2")
    #                 self.ne = QuadTree([],
    #                                    depth=self.depth - 1,
    #                                    bounding_rect=(self.cx,
    #                                                   self.bounding_rect.top,
    #                                                   self.bounding_rect.right, 
    #                                                   self.cy),
    #                                    manager = self.manager)
    #             self.ne.insert(item)
    #         if in_sw:
    #             if not self.sw:
    #                 #print("Not existing child 3")
    #                 self.sw = QuadTree([],
    #                                    depth=self.depth - 1,
    #                                    bounding_rect=(self.bounding_rect.left,
    #                                                   self.cy,
    #                                                   self.cx, 
    #                                                   self.bounding_rect.bottom),
    #                                    manager = self.manager)
    #             self.sw.insert(item)
    #         if in_se:
    #             if not self.se:
    #                 #print("Not existing child 4")
    #                 self.se = QuadTree([],
    #                                    depth=self.depth - 1,
    #                                    bounding_rect=(self.cx,
    #                                                   self.cy,
    #                                                   self.bounding_rect.right,
    #                                                   self.bounding_rect.bottom),
    #                                    manager = self.manager)
    #             self.se.insert(item)


    
    def insert_old2(self, item):
        
            """Inserts an item into the quad-tree.
        
            @param item:
                The item to insert into the quad-tree. The item must possess
                left, top, right, and bottom attributes.
            """
            
            # If the item is already in the quad-tree, return.
            if item in self.items:
                return
        
            # Check if the item belongs to any of the sub-quadrants.
            in_nw = item.left <= self.cx and item.top <= self.cy
            in_sw = item.left <= self.cx and item.bottom >= self.cy
            in_ne = item.right >= self.cx and item.top <= self.cy
            in_se = item.right >= self.cx and item.bottom >= self.cy
        
            # If the item overlaps all four quadrants, insert it at the current level.
            if in_nw and in_ne and in_se and in_sw:
                self.items.append(item)
                return
        
            # Otherwise, insert it into the appropriate sub-quadrants.
            nw_items = []
            ne_items = []
            se_items = []
            sw_items = []
        
            for existing_item in self.items:
                if existing_item.left <= self.cx:
                    if existing_item.top <= self.cy:
                        nw_items.append(existing_item)
                    if existing_item.bottom >= self.cy:
                        sw_items.append(existing_item)
                if existing_item.right >= self.cx:
                    if existing_item.top <= self.cy:
                        ne_items.append(existing_item)
                    if existing_item.bottom >= self.cy:
                        se_items.append(existing_item)
        
            if in_nw:
                nw_items.append(item)
            if in_ne:
                ne_items.append(item)
            if in_sw:
                sw_items.append(item)
            if in_se:
                se_items.append(item)
        
            # Recursively insert items into sub-quadrants.
            if nw_items:
                self.nw = QuadTree(nw_items, depth=self.depth - 1, bounding_rect=(self.bounding_rect.left, self.bounding_rect.top, self.cx, self.cy))
            if ne_items:
                self.ne = QuadTree(ne_items, depth=self.depth - 1, bounding_rect=(self.cx, self.bounding_rect.top, self.bounding_rect.right, self.cy))
            if se_items:
                self.se = QuadTree(se_items, depth=self.depth - 1, bounding_rect=(self.cx, self.cy, self.bounding_rect.right, self.bounding_rect.bottom))
            if sw_items:
                self.sw = QuadTree(sw_items, depth=self.depth - 1, bounding_rect=(self.bounding_rect.left, self.cy, self.cx, self.bounding_rect.bottom))

    
    def insert_attempt_1(self, item):
        """Inserts an item into the quad-tree.

        @param item:
            The item to insert into the quad-tree. The item must possess
            left, top, right, and bottom attributes.
        """


       #print("trying to insert in quadtree")
       #print(f"depth:{self.depth}")
       #print(f" Attempt to insert item : {item.rect}")
       #print(f"self cx : {self.cx}")
        # If the item is already in the quad-tree, return.
        if item in self.items:
            return

        # Check if the item belongs to any of the sub-quadrants.
        in_nw = item.left <= self.cx and item.top <= self.cy
        in_sw = item.left <= self.cx and item.bottom >= self.cy
        in_ne = item.right >= self.cx and item.top <= self.cy
        in_se = item.right >= self.cx and item.bottom >= self.cy

        # If the item overlaps all four quadrants, insert it at the current level.
        if in_nw and in_ne and in_se and in_sw:
            self.items.append(item)
            return

        # Otherwise, insert it into the appropriate sub-quadrants.
        if in_nw:
            if not self.nw:
                self.nw = QuadTree([], depth=self.depth - 1, bounding_rect=(self.bounding_rect.left, self.bounding_rect.top, self.cx, self.cy))
            self.nw.insert(item)
        if in_ne:
            if not self.ne:
                self.ne = QuadTree([], depth=self.depth - 1, bounding_rect=(self.cx, self.bounding_rect.top, self.bounding_rect.right, self.cy))
            self.ne.insert(item)
        if in_sw:
            if not self.sw:
                self.sw = QuadTree([], depth=self.depth - 1, bounding_rect=(self.bounding_rect.left, self.cy, self.cx, self.bounding_rect.bottom))
            self.sw.insert(item)
        if in_se:
            if not self.se:
                self.se = QuadTree([], depth=self.depth - 1, bounding_rect=(self.cx, self.cy, self.bounding_rect.right, self.bounding_rect.bottom))
            self.se.insert(item)