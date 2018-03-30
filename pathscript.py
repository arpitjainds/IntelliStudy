import xlrd
import os
from epsilon.models import Career, Course, Has

skillexcel= xlrd.open_workbook(os.path.join(os.getcwd(), 'data.xlsx'))
z = skillexcel.sheet_by_index(0)

for i in range(1, 5):
	try:
		for j in range(1,19):
			part = int(z.cell(i+1,j).value)
			print(part)
			part = part.split(",")
			if part[0] == '1':

				course_name = z.cell(1,j).value
				career_name = z.cell(i,1).value


				course = Course.objects.create(name=course_name)
				career = Career.objects.create(name=career_name)

				path = Has.objects.create(career_id=career, course_id=course, level='intermediate', order=part[2])

			else:
				continue

		print (str(i) + "done")

	except Exception as e:
		print(e)
		print(i)
