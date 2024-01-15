
from manim import *

class ZuneImageToKotlin(Scene):
    def construct(self):

        
        m0 = Matrix([[0,1],[2,3]],h_buff=1.0)
        m1 = Matrix([[4,5],[6,7]],h_buff=1.0)
        m2 = Matrix([[8,9],[10,11]],h_buff=1.0)
        m3 = Matrix([[255,255],[255,255]],h_buff=1.0) 
        # Change colors 
        m0.color = RED
        m1.color= GREEN
        m2.color= BLUE
        # # Add texts
        # t1 = Text("Red Channel")
        # t2 = Text("Green Channel")
        # t3 = Text("Blue Channel")
        # t4 = Text("Alpha Channel")
        # y = VGroup(t1,t2,t3,t4).set_x(-10).arrange(buff=1.0)
        # self.add(y)
        x = VGroup(m0, m1, m2, m3).set_x(0).arrange(buff=1.0)

        combined = Matrix([[255, 0,4,8, 255, 2, 6, 10],
                           [255, 1,5,9, 255, 3, 7, 11]])
        #combined.color()
        
        # manually add colors
        ent = combined.get_entries()
        colors = [WHITE,RED,GREEN,BLUE]
        for k in range(len(ent)):
            ent[k].set_color(colors[k % 4])
        self.add(m0)
        # self.color(3,6,combined,RED);
        # self.color(9,12,combined,RED);
        # self.color(15,18,combined,RED);

        
        self.play(Create(x))  # animate the creation of the first matrix
        self.wait()
        self.play(Transform(x, combined))  # interpolate transposition
        self.wait()
        self.play(FadeOut(combined))  
        #self.add(m1)
