
from manim import *

class OverallArchitecture(Scene):
    def construct(self):
        windows = create_box(Text("zune-image",font_size=15),
                      Text("x86-64 Windows",font_size=12))


        linux = create_box(Text("zune-image",font_size=15),Text("x86-64 Linux",font_size=12))


      
        stacked_backends = VGroup(windows,linux).set_x(0).set_y(0).arrange(DOWN,0.5)
        

        jni = create_box(Text("JNI layer",font_size=13),Text("Kotlin",font_size=12))

        jni_combined = VGroup(stacked_backends,jni).set_x(0).set_y(0).arrange(RIGHT,2.0);
        
      
        interface = create_box(Text("ZilImageInterface",font_size=13),Text("Image interface",font_size=13))

        interface_combined = VGroup(jni_combined,interface).set_x(0).set_y(0).arrange(RIGHT,2.0)
        

        android = create_box(Text("ZilAndroidBitmap",font_size=15),
                      Text("Android",font_size=12))

        desktop = create_box(Text("ZilBitmap",font_size=15),Text("Desktop",font_size=12))
        
        stacked_frontends = VGroup(android,desktop).set_x(0).set_y(0).arrange(DOWN,0.5)

        final_combined = VGroup(interface_combined,stacked_frontends).set_x(0).set_y(0).arrange(RIGHT,2.0)
        
        
        

        a1 = Arrow(start=windows.get_corner(RIGHT),end=jni.get_corner(LEFT))
        a2 = Arrow(start=linux.get_corner(RIGHT),end=jni.get_corner(LEFT))
        a3 = Arrow(start=jni.get_corner(RIGHT),end = interface.get_corner(LEFT))
        a4 = Arrow(interface.get_corner(RIGHT),android.get_corner(LEFT))
        a5 = Arrow(interface.get_corner(RIGHT),desktop.get_corner(LEFT))



        self.add(final_combined)
        self.add(a1,a2,a3,a4,a5)

        
        pass

def create_box(*args:Any):
    sq = Square(side_length=1.8)
    text = VGroup(*args).set_x(0).arrange(DOWN,0.3)
    sq.add(text)
    return sq
      
