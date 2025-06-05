# shadows.py
# rayboytim 6/4/25

from objects import *

# object shadows
class Shadow(Object):
    def __init__(self, parent):
        self.parent = parent
        
        super().__init__(parent.pos.x, parent.pos.y)

        self.radius = self.parent.minRadius

    def move(self):
        self.pos = self.parent.pos

    def draw(self, surface):
        # calculate shadow color
        alpha = 64-(self.parent.height)
        if alpha < 32:
            alpha = 32
        elif alpha > 64:
            alpha = 64

        self.color = (0, 0, 0, alpha)

        # create temp surface
        shadowSurf = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)

        # move shadow
        self.move()

        info = (
            shadowSurf,
            self.color,
            (self.radius, self.radius),
            self.radius
        )

        pygame.draw.circle(*info)

        # blit to be able to have transparency
        surface.blit(shadowSurf, (self.pos.x - self.radius, self.pos.y - self.radius))

    def getRect(self):
        return super().getRect()