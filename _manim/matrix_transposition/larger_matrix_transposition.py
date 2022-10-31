from manim import *
import numpy as np
class LargerMatrixTransposition(Scene):
    def construct(self):
        # Create our 6 by 6 array
        list_args = list(range(0,36));
        array = np.array(list_args).reshape((6,6));

        # Show our matrix
        m0 = Matrix(array,v_buff=0.9,h_buff=0.8)
        m0_entries = m0.get_entries();
        
        # Manually add colors
        self.color(3,6,m0_entries,RED);
        self.color(9,12,m0_entries,RED);
        self.color(15,18,m0_entries,RED);

        m1 = Matrix(array.T,v_buff=0.9,h_buff=0.8)
        m1_entries = m1.get_entries();        
        
        self.color(18,21,m1_entries,YELLOW);
        self.color(24,27,m1_entries,YELLOW);
        self.color(30,33,m1_entries,YELLOW);

        a1 = Arrow(start=LEFT,end=RIGHT)

        g = Group(
            m0,a1,m1
        ).arrange_in_grid(cols=3,buff=1)
        
        self.add(g)

    def color(self,start,stop,group:VGroup,color):
        for i in range(start,stop):
            group[i].set_color(color)

