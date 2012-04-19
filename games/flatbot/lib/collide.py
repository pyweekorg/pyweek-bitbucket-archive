
class Collider(object):
    def do_land(self, dy):
        pass

    def do_hitwall(self, dx):
        pass

    def do_collision(self, cell, rect, o_b, o_t, o_l, o_r, dy, ody, dx, odx):
        g = cell.tile.properties.get
        self.resting = False
        if (g('top') and o_b >= cell.top and rect.bottom < cell.top):
            rect.y = cell.top
            self.dy = 0
            if ody: self.do_land(dy)
        if (g('left') and o_r <= cell.left and rect.right > cell.left):
            rect.x = cell.left - rect.width
            self.dx = 0
            if odx: self.do_hitwall(dx)
        if (g('right') and o_l >= cell.right and rect.left < cell.right):
            rect.x = cell.right
            if odx: self.do_hitwall(dx)
            self.dx = 0
        if (g('bottom') and o_t <= cell.bottom and rect.top > cell.bottom):
            self.dy = 0
            rect.y = cell.bottom - rect.height

