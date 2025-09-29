#!/usr/bin/env python3
"""
Simple test to verify tkinter is working properly
"""
import tkinter as tk

def test_tkinter():
    root = tk.Tk()
    root.title("Tkinter Test")
    root.geometry("400x300")
    
    # Create a simple canvas
    canvas = tk.Canvas(root, width=400, height=300, bg="black")
    canvas.pack()
    
    # Draw something simple
    canvas.create_rectangle(50, 50, 350, 250, fill="blue", outline="white", width=2)
    canvas.create_text(200, 150, text="Tkinter Test", fill="white", font=("Arial", 20, "bold"))
    
    # Make sure window is visible
    root.lift()
    root.attributes('-topmost', True)
    root.after(100, lambda: root.attributes('-topmost', False))
    
    print("Window should be visible now. Close it to continue.")
    root.mainloop()

if __name__ == "__main__":
    test_tkinter()
