import xlrd
import os
from epsilon.models import Question, Option, Course, Content

skillexcel= xlrd.open_workbook(os.path.join(os.getcwd(), 'data.xlsx'))
z = skillexcel.sheet_by_index(0)

for i in range(0, 20):
	try:
		course = Course.objects.get(name='Blockchain')
		content = Content.objects.get(course_id=course, name='Bitcoin')
		question = z.cell(i, 0).value
		print(question)
		level = z.cell(i, 7).value
		print(level)
		option_a = z.cell(i, 1).value
		option_b = z.cell(i, 2).value
		option_c = z.cell(i, 3).value
		option_d = z.cell(i, 4).value
		option_e = z.cell(i, 5).value

		answer = z.cell(i,6).value
		print(answer)

		if level == 'b' :
				level = 'beginner'
		elif level == 'i' :
				level = 'intermediate'
		else :
				level = 'advanced'

		quiz = Question.objects.create(
				content_id = content,
				level = level,
				question = question,
				answer = answer

			)
		print(quiz)
		options = Option.objects.create(
				question_id = quiz,
				option_a = option_a,
				option_b = option_b,
				option_c = option_c,
				option_d = option_d,
				option_e = option_e
			)

		print (str(i) + "done")

	except Exception as e:
		print(e)
		print(i)
