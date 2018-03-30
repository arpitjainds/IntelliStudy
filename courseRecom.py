import xlrd
import os

skillexcel= xlrd.open_workbook(os.path.join(os.getcwd(), 'data.xlsx'))
z = skillexcel.sheet_by_index(0)
arr = []
for i in range(1, 16):
	row = []
	try:
		for j in range(0,19):
			row.append(int(z.cell(i,j+1).value))

	except Exception as e:
		print(e)
		print(i)
	arr.append(row)
	
print(arr)