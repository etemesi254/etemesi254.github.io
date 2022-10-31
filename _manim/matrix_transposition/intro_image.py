from manim import *

class SimpleMatrixTransposition(Scene):
    def construct(self):
        m0 = Matrix([[1,2, 3], [4, 5,6],[7,8,9]])
        m0.add(SurroundingRectangle(m0.get_columns()[0],color=RED))

        m1 = Matrix([[1,4,7],[2,5,8],[3,6,9]])
        a1 = Arrow(start=LEFT,end=RIGHT)

        m1.add(SurroundingRectangle(m1.get_rows()[0],color=RED))
        
        self.play(Create(m0))  # animate the creation of the first matrix
        self.wait()
        self.play(Transform(m0, m1))  # interpolate transposition
        self.wait()
        self.play(FadeOut(m1))  # fade 
      