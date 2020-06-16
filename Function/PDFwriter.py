from parapy.core import *
import matplotlib.pyplot as plt
import numpy as np
import os
from parapy.core.validate import *
from parapy.core.decorators import action
from parapy.gui.image import Image
from Function.help_fucntions import *
from fpdf import FPDF


class PDFwriter(Base):
    # path to files storing the output
    res = Input()

    @action(label='Export PDF')
    def printPDF(self):
        self.output_images[0].write('Output/test1.png')
        self.output_images[1].write('Output/test2.png')
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        pdf.image('Output/test1.png', 10, 10)
        pdf.output('Output/testpdf.pdf', 'F')