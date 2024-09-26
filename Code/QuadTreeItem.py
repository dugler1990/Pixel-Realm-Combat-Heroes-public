import pygame
class QuadTreeItem(object):
    def __init__(self, left, top, right, bottom,_id=-1, colour=(255, 255, 255)):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom
        self.colour = colour
        self.id = _id
        
    # def draw(self):
    #     x = self.left
    #     y = self.top
    #     w = self.right - x
    #     h = self.bottom - y
    #     pygame.draw.rect(screen, self.colour, pygame.Rect(x, y, w, h), 2)
