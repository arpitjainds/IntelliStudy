import xlrd
import os
from epsilon.models import Career, Course, Has

skillexcel= xlrd.open_workbook(os.path.join(os.getcwd(), 'data.xlsx'))
z = skillexcel.sheet_by_index(0)
arr = []
for i in range(1, 16):
	row = []
	try:
		for j in range(0,18):
			print("career",z.cell(i,0).value)
			print(z.cell(i,j+1).value)
			row.append(int(z.cell(i,j+1).value))
			print("\n")
	
		print (str(i) + "done")


	except Exception as e:
		print(e)
		print(i)
	arr.append(row)
	
print(arr)