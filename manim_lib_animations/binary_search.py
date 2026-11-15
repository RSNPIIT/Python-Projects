from manim import *

class BinarySearchDemo(Scene):
    def construct(self):
        # This is the Introduction Scene for the rest of Animatronic Video
        intro_title = Text("Binary Search Algorithm", font_size=48, color=BLUE)
        intro_subtitle = Text("Time Complexity: O(log n)", font_size=28, color=GRAY).next_to(intro_title, DOWN, buff=0.4)

        self.play(Write(intro_title), FadeIn(intro_subtitle))
        self.wait(1.5)
        self.play(FadeOut(intro_title), FadeOut(intro_subtitle))

        # Sorted array to search through
        arr = [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]

        # Run all three cases back-to-back in one video
        self.run_search(arr, target=16, case_title="Case 1: Middle Element (Best Case - Target: 16)")
        self.run_search(arr, target=2,  case_title="Case 2: Edge Element (First Index - Target: 2)")
        self.run_search(arr, target=56, case_title="Case 3: Somewhere in Between (Target: 56)")

    def run_search(self, arr, target, case_title):
        self.clear()  # Clear previous case from screen

        # 1. Title & Status Header
        title = Text(case_title, font_size=32, color=BLUE).to_edge(UP)
        status = Text("Initializing pointers...", font_size=24, color=WHITE).next_to(title, DOWN, buff=0.4)
        self.play(Write(title), FadeIn(status))

        # 2. Build the Array Boxes
        boxes = VGroup()
        labels = VGroup()
        indices = VGroup()

        for i, val in enumerate(arr):
            box = Square(side_length=0.95, color=WHITE, stroke_width=2)
            num = Text(str(val), font_size=26).move_to(box.get_center())
            idx = Text(str(i), font_size=18, color=GRAY).next_to(box, DOWN, buff=0.15)
            
            boxes.add(box)
            labels.add(num)
            indices.add(idx)

        # Arrange boxes horizontally in the center
        array_group = VGroup()
        for i in range(len(arr)):
            cell = VGroup(boxes[i], labels[i], indices[i])
            array_group.add(cell)
        array_group.arrange(RIGHT, buff=0.1).move_to(ORIGIN)

        self.play(Create(boxes), Write(labels), FadeIn(indices))
        self.wait(0.5)

        # 3. Create Pointers (Low, Mid, High)
        low, high = 0, len(arr) - 1
        
        low_ptr = Text("L", font_size=24, color=GREEN).next_to(boxes[low], UP, buff=0.25)
        high_ptr = Text("H", font_size=24, color=RED).next_to(boxes[high], UP, buff=0.25)
        mid_ptr = Text("M", font_size=24, color=YELLOW).next_to(boxes[0], UP, buff=0.65)

        self.play(FadeIn(low_ptr), FadeIn(high_ptr))

        # 4. Binary Search Animation Loop
        while low <= high:
            mid = (low + high) // 2

            # Move Mid pointer & highlight current Mid box
            new_status = Text(f"Checking Mid index {mid} (Value: {arr[mid]})", font_size=24)
            new_status.next_to(title, DOWN, buff=0.4)

            if mid_ptr not in self.mobjects:
                mid_ptr.next_to(boxes[mid], UP, buff=0.65)
                self.play(
                    Transform(status, new_status),
                    FadeIn(mid_ptr),
                    boxes[mid].animate.set_fill(YELLOW, opacity=0.35)
                )
            else:
                self.play(
                    Transform(status, new_status),
                    mid_ptr.animate.next_to(boxes[mid], UP, buff=0.65),
                    boxes[mid].animate.set_fill(YELLOW, opacity=0.35)
                )
            self.wait(0.8)

            # Check if Target is Found
            if arr[mid] == target:
                found_status = Text(f"Found {target} at index {mid}!", font_size=26, color=GREEN)
                found_status.next_to(title, DOWN, buff=0.4)
                self.play(
                    Transform(status, found_status),
                    boxes[mid].animate.set_fill(GREEN, opacity=0.6).set_color(GREEN)
                )
                self.wait(1.5)
                break

            # Target is in the RIGHT half -> Eliminate Left half
            elif arr[mid] < target:
                eliminated = [
                    boxes[i].animate.set_opacity(0.2) for i in range(low, mid + 1)
                ] + [
                    labels[i].animate.set_opacity(0.2) for i in range(low, mid + 1)
                ]
                low = mid + 1
                
                step_text = Text(f"{arr[mid]} < {target} → Move Low to index {low}", font_size=24, color=ORANGE)
                step_text.next_to(title, DOWN, buff=0.4)
                
                self.play(
                    Transform(status, step_text),
                    *eliminated,
                    low_ptr.animate.next_to(boxes[low], UP, buff=0.25)
                )

            # Target is in the LEFT half -> Eliminate Right half
            else:
                eliminated = [
                    boxes[i].animate.set_opacity(0.2) for i in range(mid, high + 1)
                ] + [
                    labels[i].animate.set_opacity(0.2) for i in range(mid, high + 1)
                ]
                high = mid - 1
                
                step_text = Text(f"{arr[mid]} > {target} → Move High to index {high}", font_size=24, color=ORANGE)
                step_text.next_to(title, DOWN, buff=0.4)
                
                self.play(
                    Transform(status, step_text),
                    *eliminated,
                    high_ptr.animate.next_to(boxes[high], UP, buff=0.25)
                )

            self.wait(0.6)

