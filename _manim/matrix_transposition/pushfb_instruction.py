from manim import *
import numpy as np
class PushfbInstruction(Scene):
    def construct(self):
      
        t0 = Text("SSE register",font_size=20);
        m0 = Matrix([[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]],h_buff=0.85)
        t1 = Text("SSE register 2",font_size=20)
        m1 = Matrix([[15,7,14,6,13,5,12,4,11,3,10,2,9,1,8,0]],h_buff=0.85)
        m3 = Matrix([[15,7,14,6,13,5,12,4,11,3,10,2,9,1,8,0]],h_buff=0.85)
        
     
        g = Group(
            t0,m0,t1,m1,m3
        ).arrange_in_grid(cols=1,buff=1)
        
        self.add(g)
        