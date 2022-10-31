from manim import *

class SimpleMatrixTransposition(Scene):
    def construct(self):
        m0 = Matrix([[1,2, 3], [4, 5,6],[7,8,9]])
        m0.add(SurroundingRectangle(m0.get_columns()[0],color=RED))

        m1 = Matrix([[1,4,7],[2,5,8],[3,6,9]])
        a1 = Arrow(start=LEFT,end=RIGHT)

        m1.add(SurroundingRectangle(m1.get_rows()[0],color=RED))
        g = Group(
            m0,a1,m1
        ).arrange_in_grid(cols=3,buff=1)
        
        self.add(g)