from TexSoup import TexSoup
import yaml
import sys

def check_department_number(soup, good_department_number):
	lis = list(soup.find_all('Center'))
	deparment_string = lis[1].string.strip()
	if "КАФЕДРА №" in deparment_string:
		try:
			department_number = int(deparment_string.split("КАФЕДРА №",1)[1])
		except ValueError:
			return False
		if department_number == good_department_number:
			return True
		else:
			return False
	else:
		return False

def check_course_name(soup, good_course_name):
	texts = list(soup.find_all('Centering'))
	course_name = texts[7].string.strip()
	if "по курсу:" in course_name:
		course_name = course_name.split("по курсу:",1)[1].strip()
		if course_name.lower() == good_course_name.lower():
			return True
		else:
			return False
	else:
		return False

def check_teacher_name(soup, good_teacher_name):
	texts = list(soup.find_all('Centering'))
	teacher_name = texts[1].string.strip()
	if teacher_name == good_teacher_name:
		return True
	else:
		return False

def check_teacher_position(soup, good_teacher_position):
	texts = list(soup.find_all('Centering'))
	teacher_position = texts[0].string.strip()
	if teacher_position == good_teacher_position:
		return True
	else:
		return False

def check_report_number(soup, good_report_number):
	texts = list(soup.find_all('Centering'))
	report_number_string = texts[5].string.strip()
	if "ОТЧЕТ О ЛАБОРАТОРНОЙ РАБОТЕ №" in report_number_string:
		try:
			report_number = int(report_number_string.split("ОТЧЕТ О ЛАБОРАТОРНОЙ РАБОТЕ №",1)[1])
		except ValueError:
			return False
		if report_number == good_report_number:
			return True
		else:
			return False
	else:
		return False

def check_report_name(soup, good_report_name):
	texts = list(soup.find_all('Centering'))
	report_name = texts[6].string.strip()
	if report_name.lower() == good_report_name.lower():
		return True
	else:
		return False

def main():
	if len(sys.argv) == 3:
		filename = sys.argv[1]
		config_file = sys.argv[2]
	else:
		filename = 'titlepage.tex'
		config_file = 'config.yaml'
	print("Current latex file: ",filename)
	print("Current config file: ",config_file)
	print ("")

	with open(filename) as latex_file:
		try:
			soup = TexSoup(latex_file)
		except TypeError:
			print ("Invalid Latex file. exit...")
			exit()
	with open(config_file) as stream:
		try:
			config = yaml.safe_load(stream)
		except yaml.YAMLError as exc:
			print(exc)

	result_check_department_number = check_department_number(soup,config['department_number'])
	result_check_course_name = check_course_name(soup, config['course_name'])
	result_check_report_name = check_report_name(soup, config['report_name'])
	result_check_report_number = check_report_number(soup, config['report_number'])
	result_check_teacher_name = check_teacher_name(soup, config['teacher']['name'])
	result_check_teacher_position = check_teacher_position(soup, config['teacher']['position'])

	print ("Confirmed department number: ",result_check_department_number)
	print ("Confirmed course name: ",result_check_course_name)
	print ("Confirmed report name: ",result_check_report_name)
	print ("Confirmed report number: ",result_check_report_number)
	print ("Confirmed teacher name: ",result_check_teacher_name)
	print ("Confirmed teacher position: ",result_check_teacher_position)

	print ("")
	if result_check_department_number and result_check_course_name and result_check_report_name and result_check_report_number and result_check_teacher_name and result_check_teacher_position:
		print ('[+] Good titlepage')
		# print ('return 0')
		return 0
	else:
		print ('[-] Titlepage contains mistakes')
		# print ('return 1')
		return 1

if __name__ == "__main__":
    main()