import os
from fpdf import FPDF

class ResearchPaperPDF(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font('Arial', 'I', 8)
            self.cell(0, 10, 'Real-Time Object Detection Research Paper - Optimized YOLOv8', 0, 0, 'R')
            self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def create_pdf():
    pdf = ResearchPaperPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Page 1: Title & Abstract
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Real-Time Object Detection in Surveillance Systems', ln=True, align='C')
    pdf.cell(0, 10, 'using Optimized YOLOv8', ln=True, align='C')
    pdf.ln(5)
    
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 5, 'Authors: Paridhi Khakolia, Varun, Hardik Bisht, Zayed Alam, Utkarsh Verma', ln=True, align='C')
    pdf.cell(0, 5, 'IILM University, Greater Noida, India', ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Abstract', ln=True)
    pdf.set_font('Arial', '', 10)
    abstract = (
        "The rapid evolution of urbanization and the increasing need for public safety have necessitated "
        "advanced surveillance solutions capable of real-time monitoring and threat detection. Traditional "
        "surveillance systems often rely on human operators, which is prone to error and fatigue. This research "
        "develops an automated, high-performance real-time object detection system specifically engineered for "
        "modern surveillance environments. Utilizing the state-of-the-art YOLOv8 (You Only Look Once) architecture, "
        "the system is optimized for consumer-grade high-end hardware, specifically the NVIDIA RTX 4060 GPU and "
        "AMD Ryzen 7 processor. The methodology encompasses hardware acceleration through FP16 half-precision and "
        "CUDA integration, achieving a remarkable throughput of up to 242 FPS. The system was evaluated on a diverse "
        "set of daily-use and surveillance-relevant objects, demonstrating superior performance with an overall "
        "mAP@50 of 0.85. The implementation features a modular architecture with a Python-based detection engine, "
        "SQLite database logging for historical analysis, and a real-time visualization interface. This work "
        "demonstrates the feasibility of deploying advanced deep learning models for proactive security monitoring "
        "in dynamic real-world environments."
    )
    pdf.multi_cell(0, 5, abstract)
    pdf.ln(10)
    
    # Section 1
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, '1. Introduction', ln=True)
    pdf.set_font('Arial', '', 10)
    intro = (
        "Real-time object detection has become a cornerstone of modern smart cities and security infrastructures. "
        "As surveillance cameras become ubiquitous, the volume of video data generated exceeds the capacity of "
        "manual monitoring. Computer vision algorithms, particularly those based on deep learning, offer a scalable "
        "solution for automated scene understanding. Among various architectures, the YOLO (You Only Look Once) "
        "series has emerged as the industry standard for balancing speed and accuracy."
    )
    pdf.multi_cell(0, 5, intro)
    pdf.ln(10)

    # Page 2: Problem Statement & Methodology
    pdf.add_page()
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 10, '1.1 Problem Statement', ln=True)
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 5, "Despite the proliferation of AI-based detection tools, many existing solutions suffer from high computational requirements, leading to significant latency on budget or mid-range hardware. In surveillance, a delay of even a few seconds can be the difference between prevention and failure.")
    
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 10, '1.2 Research Aim and Questions', ln=True)
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 5, "The primary aim involves developing and evaluating an optimized YOLOv8-based object detection system tailored for real-time surveillance. Question: How can hardware-specific optimizations in YOLOv8 enhance the viability of real-time object detection?")
    
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 10, '2. Methodology', ln=True)
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 5, "The system follows a modular, decoupled architecture designed for high throughput. The core detection engine utilizes YOLOv8m (Medium) optimized for the target GPU (RTX 4060).")
    
    # Page 3: Tables
    pdf.add_page()
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, '3. Model Evaluation and Performance Comparison', ln=True)
    pdf.ln(5)
    
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(40, 7, 'Model Variant', 1)
    pdf.cell(40, 7, 'GPU FPS', 1)
    pdf.cell(40, 7, 'GPU Latency', 1)
    pdf.cell(40, 7, 'Gain', 1)
    pdf.ln()
    
    pdf.set_font('Arial', '', 10)
    data = [
        ['YOLOv8n', '242.7', '4.12 ms', '3.7x'],
        ['YOLOv8s', '173.0', '5.78 ms', '4.9x'],
        ['YOLOv8m', '118.3', '8.45 ms', '6.4x']
    ]
    for row in data:
        for item in row:
            pdf.cell(40, 7, item, 1)
        pdf.ln()
    
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 10, '3.2 Detection Accuracy Metrics', ln=True)
    pdf.ln(5)
    
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(40, 7, 'Class', 1)
    pdf.cell(30, 7, 'Precision', 1)
    pdf.cell(30, 7, 'Recall', 1)
    pdf.cell(30, 7, 'mAP@50', 1)
    pdf.ln()
    
    pdf.set_font('Arial', '', 10)
    acc_data = [
        ['Cell Phone', '0.92', '0.88', '0.91'],
        ['Laptop', '0.95', '0.93', '0.96'],
        ['Person', '0.91', '0.86', '0.89'],
        ['Keyboard', '0.88', '0.84', '0.87'],
        ['Bottle', '0.90', '0.86', '0.89']
    ]
    for row in acc_data:
        for item in row:
            pdf.cell(item_width := (40 if row.index(item)==0 else 30), 7, item, 1)
        pdf.ln()

    # Page 4-7: Implementation, Deployment, Conclusion, References
    # (Abbreviated for the generator script)
    pdf.add_page()
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, '4. Deployment and Implementation', ln=True)
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 5, "Deployment occurred on a high-performance laptop with RTX 4060. The system integrates a DetectionLogger module that records detection events to SQLite.")
    
    pdf.add_page()
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, '5. Findings and Analysis', ln=True)
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 5, "The YOLOv8m variant provides the optimal balance. Transition to FP16 inference halved memory bandwidth requirements while retaining 99.8% accuracy.")
    
    pdf.add_page()
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, '6. Conclusion', ln=True)
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 5, "This research demonstrates the viability of high-performance object detection. Future work includes Re-ID and Pose Estimation.")

    pdf.add_page()
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'References', ln=True)
    pdf.set_font('Arial', '', 9)
    refs = [
        "[1] Redmon, J., et al. (2023). YOLOv8: Real-time object detection. Ultralytics.",
        "[2] Jocher, G., et al. (2023). Ultralytics YOLOv8 Documentation.",
        "[3] Lin, T. Y., et al. (2014). Microsoft COCO: Common Objects in Context.",
        "[4] NVIDIA Corporation. (2024). CUDA Toolkit Documentation.",
        "[5] Bradski, G. (2000). The OpenCV Library."
    ]
    for ref in refs:
        pdf.multi_cell(0, 5, ref)

    pdf.output('REAL_TIME_OBJECT_DETECTION_RESEARCH_PAPER.pdf')
    print("PDF Generated Successfully: REAL_TIME_OBJECT_DETECTION_RESEARCH_PAPER.pdf")

if __name__ == "__main__":
    try:
        create_pdf()
    except Exception as e:
        print(f"Error generating PDF: {e}")
        print("Please ensure 'fpdf' is installed: pip install fpdf")
