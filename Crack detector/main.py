# This is correct code no 3 
import cv2
# import numpy as np
import os

class CrackAnalyzerDSA:

    def __init__(self):
        # --- DSA CONCEPT 1: HASH MAP (Dictionary) ---
        self.crack_database = {}
        
        # OpenCV Preprocessing Parameters
        self.min_area = 100       
        self.block_size = 51  
        self.c_value = 10     
        self.morph_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5)) #fine tuning

        # Severity Thresholds
        self.medium_span_pct = 10.0  
        self.high_span_pct = 25.0 
        self.critical_span_pct = 40.0 
#seveerity evaluation
    def evaluate_severity(self, max_span_pct):
        # if max_span_pct == 0: 
        #     return "Clear", (0, 255, 0)   #Blue,green,red  #mixing for highlighting colors,to read   
        # if max_span_pct >= self.critical_span_pct: 
        #     return "CRITICAL", (0, 0, 255)   
        if max_span_pct >= self.high_span_pct: 
            return "High", (0, 165, 255)     
        elif max_span_pct >= self.medium_span_pct: 
            return "Medium", (0, 255, 255)   
        else: 
            return "Low", (255, 255, 0)      
#it saves data
    def save_data(self, location_id, severity, span_pct):
        self.crack_database[location_id] = {
            "Severity": severity,
            "Damage_Span": f"{span_pct:.1f}%",
            "Action": "Fix Immediately!" if severity == "CRITICAL" else "Monitor"
        }
#analyze and process frame
    def process_frame(self, frame, location_id="Unknown_Location"):
        annotated_frame = frame.copy() #makes a copy to draw warning labels
        img_h, img_w = frame.shape[:2] #set dimensions of picture
        max_img_dim = max(img_h, img_w) #finding exact height and width
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) #make pic black and white
        blurred = cv2.bilateralFilter(gray, 9, 75, 75)   # blur to ignore roughness
        
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY_INV, self.block_size, self.c_value #dark turns white, restroad is pitch black
        )
        
        closed_cracks = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, self.morph_kernel) #morphological closing
        contours, _ = cv2.findContours(closed_cracks, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) #comma and dash unpacking
        
        longest_crack_span = 0
        
        # --- DSA CONCEPT 2: O(N) LINEAR TRAVERSAL ---  visiting every element in a sequence
        total_damage_area = 0
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > self.min_area:
                total_damage_area += area 

# Then calculate percentage based on the total image area
        image_area = img_h * img_w
        area_percentage = (total_damage_area / image_area) * 100

        severity_label, text_color = self.evaluate_severity(area_percentage)
        self.save_data(location_id, severity_label, area_percentage)
        
        cv2.rectangle(annotated_frame, (0, 0), (300, 80), (30, 30, 30), -1)
        cv2.putText(annotated_frame, severity_label, (20, 55), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, text_color, 4)
                    
        return annotated_frame
#single image analyzer
    def analyze_single_image(self, image_path):
        if not os.path.exists(image_path):
            print(f"Error: '{image_path}' not found.")
            return

        img = cv2.imread(image_path)
        if img is None: return

        max_dim = 1000
        h, w = img.shape[:2]
        if h > max_dim or w > max_dim:
            scale = max_dim / float(max(h, w))
            img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)

        filename = os.path.basename(image_path)
        result = self.process_frame(img, location_id=filename)
        
        print("\n--- SCAN COMPLETE ---")
        print(f"Dictionary Database Output: {self.crack_database[filename]}")
        print("Press ANY KEY on the image window to close it.")
        
        cv2.imshow(f"Analysis - {filename}", result)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def analyze_folder(self, folder_name):
        if not os.path.exists(folder_name):
            print(f"Error: '{folder_name}' not found.")
            return

        valid_exts = ('.jpg', '.jpeg', '.png', '.bmp')
        
        # --- DSA CONCEPT 3: DYNAMIC ARRAY WITH INDEX POINTER ---  allocated in heap memory(shared region of RAM)

        image_list = []
        for f in os.listdir(folder_name):
            if f.lower().endswith(valid_exts):
                image_list.append(os.path.join(folder_name, f))

        total_images = len(image_list)
        if total_images == 0: 
            return print("No images found.")

        print(f"\nLoaded {total_images} images into the Array.")
        print("CONTROLS: 'N' for Next, 'P' for Previous, 'Q' to Quit\n")

        # Initialize the Index Pointer
        current_index = 0

        while current_index < total_images:
            current_image_path = image_list[current_index]
            img = cv2.imread(current_image_path)
            
            if img is not None:
                max_dim = 1000
                h, w = img.shape[:2]
                if h > max_dim or w > max_dim:
                    scale = max_dim / float(max(h, w))
                    img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)

                filename = os.path.basename(current_image_path)
                result = self.process_frame(img, location_id=filename)
                
                # Update window title to show exactly where we are in the array
                window_title = f"Batch Mode ({current_index + 1}/{total_images}) - Press N/P/Q"
                cv2.imshow(window_title, result)
            
            while True:
                key = cv2.waitKey(0) & 0xFF
                if key == ord('n') or key == ord('N'):
                    cv2.destroyAllWindows()
                    current_index += 1  # Move pointer forward
                    break 
                elif key == ord('p') or key == ord('P'):
                    cv2.destroyAllWindows()
                    # Move pointer backward, but prevent it from crashing if we are at 0
                    current_index = max(0, current_index - 1)
                    break
                elif key == ord('q') or key == ord('Q'):
                    cv2.destroyAllWindows()
                    print("\nBatch processing terminated early.")
                    self.print_final_database()
                    return 
                    
        cv2.destroyAllWindows()
        print("\nArray traversal complete.")
        self.print_final_database()

    def print_final_database(self):
        print("\n" + "="*50)
        print("📊 FINAL CRACK DICTIONARY DATABASE:")
        print("="*50)
        for loc, data in self.crack_database.items():
            print(f"ID: {loc} | Data: {data}")
        print("="*50 + "\n")

# --- Main Execution Block ---
if __name__ == "__main__":
    Analyzer = CrackAnalyzerDSA()
    print("--- Road Crack Detection System ---")
    print("1. Analyze a single image")
    print("2. Process a dataset folder")
    
    choice = input("\nSelect mode (1/2): ")
    if choice == '1': 
        file_path = input("Enter the exact image file path : ")
        Analyzer.analyze_single_image(file_path)
    elif choice == '2': 
        folder_path = input("Enter the exact folder name : ")
        Analyzer.analyze_folder(folder_path)
    else: 
        print("Invalid choice.") 