import pymupdf
src=pymupdf.open("Proposed_Floor_Plan-20260916-R26.pdf"); sq=pymupdf.open("Servant_Quarters-SQ-PP-05.pdf")
out=pymupdf.open()
out.insert_pdf(src,from_page=0,to_page=0)      # basement
out.insert_pdf(sq,from_page=0,to_page=0)       # servant quarters
out.insert_pdf(src,from_page=1,to_page=4)      # ground, first, second, terrace
out.save("Proposed_Floor_Plan-20260916-R26-SET.pdf"); print("set", len(out))
