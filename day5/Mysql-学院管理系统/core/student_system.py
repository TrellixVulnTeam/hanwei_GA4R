#!/usr/bin/env python
# _*_ encoding:utf-8 _*_
__author__ = "han"
import sys,os
path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(path)

import hashlib,webbrowser

from core import db_sql

class View_Interface(object):
    def __int__(self):
        self.Is_Login = False
        self.Login_User = None
        self.DB = db_sql.DB_Control()


    def Menu(self):
        '''
        主页
        :return: 
        '''
        menu_list = ['1.用户登录','2.注册用户']
        menu_dict = {
            '1.用户登录':self.Login,
            '2.注册用户':self.Register
        }
        while True:
            print('学员管理系统'.center(50,'-'))
            for menu in menu_list:
                print(menu)
            act = input("请选择(q推出)：")
            if act.isdigit() and int (act) <= len(menu_list) and len(menu_list) >0:
                func = menu_dict[menu_list[int(act)-1]]
                func()
                break
            elif act.strip() =='q':
                exit()
            else:
                print('选择错误！')
                continue
        self.Menu_For_Type()

    def Login(self):
        '''
        登陆接口
        :return: 
        '''
        while True:
            print("用户登录".center(50,'-'))
            username = input('请输入用户民：')
            password = input ('请输入密码：')
            password = self.Create_Pwd(password)
            table = self.DB.Tables['user']
            user_obj = self.DB.Session.query(table).filter(table.name==username).filter(table.pwd==password).first()
            if user_obj is None:
                print('\033[32m登录失败\033[0m')
                continue
            else:
                self.Is_Login = True
                self.Login_User = user_obj
                print('欢迎[%s]%s'%(user_obj.type.name,user_obj.name))
                break
        return self.Is_Login




    def Register(self):
        '''
        注册用户
        :return: 
        '''
        table = self.DB.Tables['user']
        user_info = {
            'name':'',
            'pwd':'',
            'qq':'',
            'email':''
        }
        while True:
            print('注册用户'.center(50,'-'))
            if user_info['name'] == '':
                username = input('请输入用户名:')
                user_obj = self.DB.Session.query(table).filter(table.name==username).first()
                if user_obj is not None:
                    print('用户名已经存在,请重新输入:')
                    continue
                else:
                    user_info['name'] = username
            else:
                password = input('请输入密码:')
                re_password = input('请再次输入密码:')
                if password != re_password:
                    print('两次密码不一致,请重新输入!')
                    continue
                else:
                    password = self.Create_Pwd(password)
                    user_info['pwd'] = password
                    qq = input('请输入QQ号:')
                    email = input('请输入邮箱账号:')
                    user_info['qq'] = qq
                    user_info['email'] = email
                    break
        type_obj_dict = self.Get_Role_Type()
        new_user = table(name=user_info['name'],pwd=user_info['pwd'],qq=user_info['qq'],email=user_info['email'])
        while True:
            print('注册类型'.center(50,'-'))
            type_list = []
            count = 1
            for type_obj in type_obj_dict:
                if type_obj_dict[type_obj].name != 'admin':
                    print(count,'.',type_obj_dict[type_obj].name)
                    type_list.append(type_obj_dict[type_obj].name)
                    count +=1
            act = input('请选择:').strip()
            if act.isdigit() and int(act) <= len(type_list) and len(act) >0:
                new_user.type = type_obj_dict[type_list[int(act)-1]]
                break
            else:
                print('选择错误!')
                continue
        self.DB.Session.add(new_user)
        self.DB.Session.commit()



    def Create_Pwd(self,pwd):
        return hashlib.md5(pwd.encode('utf8')).hexdigest()

##
    def Menu_For_Type(self):
        '''
        第二主页
        :return: 
        '''
        if self.Login_User is None:
            self.Login()
            self.Menu_For_Type()
        else:
            role_type = self.Login_User.type.name
            menu_dict = {
                'student':self.Menu_Student,
                'tacher':self.Menu_Teacher,
                'admin':self.Menu_Admin
            }
            if role_type in menu_dict:
                menu_dict[role_type]()
            else:
                print('角色类型错误！')
                exit()


##

    def Menu_Admin(self):
        '''
        管理员接口
        :return: 
        '''
        if self.Is_Login is False:
            print('用户没有登录!')
            exit()
        menu_list = ['1.创建学校','2.创建课程']
        menu_dict = {
            '1.创建学校':self.Create_School,
            '2.创建课程':self.Create_Course
        }
        while True:
            print(('欢迎管理员%s登录'%self.Login_User.name)).center(50,'-')
            for menu in menu_list:
                print(menu)
            act = input('请选择:(q推出)')
            if act.isdigit() and int(act) <= len(menu_dict) and int(act) >0:
                func = menu_dict[menu_list[int(act)-1]]
                func()
            elif act == 'q':
                self.Is_Login = False
                self.Login_User = None
                break
            else:
                print('\033[32m选择错误!\033[0m')
                continue
        self.Menu()

    def Create_School(self):
        '''
        创建学校
        :return: 
        '''
        while True:
            print('创建学校'.center(50,'-'))
            name = input('请输入学校名称:')
            address = input('请输入学校地址:')
            table = self.DB.Tables['school']
            school_obj = self.DB.Session.query(table).filter(table.name == name).first()
            if school_obj is None:
                new_school = table(name=name,address=address)
                self.DB.Session.add(new_school)
                self.DB.Session.commit()
                print('学校%s创建成功!'%new_school.name)
                break
            else:
                print('学校%s已经被创建,地址:%s'%(school_obj.name,school_obj.address))
                continue
        return  new_school



    def Create_Course(self):
        '''
        创建课程
        :return: 
        '''
        print('创建课程'.center(50),'-')
        name = input('请输入课程名称:')
        table = self.DB.Tables['course']
        choose_school = self.Sel_School()
        choose_teacher = self.Sel_Teacher()
        while True:
            price = input('请输入课程价格：')
            if price.isdigit():break
            else:
                print("价格必须是数字!")
                continue
        new_coures = table(name=name,school = choose_school,teacher=choose_teacher,price=price)
        self.DB.Session.add(new_coures)
        self.DB.Session.commit()





###

    def Menu_Teacher(self):
        '''
        教师接口
        :return: 
        '''
        if self.Is_Login is False:
            print('请重新登录！')
            exit()
        menu_list = ['1.创建班级','2.创建学员','3.开始上课','批改作业']
        menu_dict = {
            '1.创建班级':self.Create_Class,
            '2.选择学员':self.Choose_Student,
            '3.开始上课':self.Start_Class,
            '4,批改作业':self.Homework_Correcting
        }
        while True:
            print('欢迎%s老师登录工作台'%self.Login_User.name).center(50,'-')
            for menu in menu_list:
                print(menu)
            act = input('请选择(q推出)')
            if act.isdigit() and int(act) <=len(menu_dict) and int(act)>0:
                func = menu_dict[menu_list[int(act)-1]]
                func()
            elif act == 'q':
                self.Is_Login = False
                self.Login_User = None
                break

            else:
                print('\033[35m选择错误!\033[0m')
                continue
        self.Menu()


    def Create_Class(self):
        '''
        创建班级
        :return: 
        '''
        res = False
        table = self.DB.Tables['class']
        print('请为班级选择课程')
        choose_coures = self.Sel_Course()
        if choose_coures is None:
            res = False
        else:
            class_name = input("请输入班级名称：")
            new_class = table(name=class_name,course=choose_coures)
            self.DB.Session.add(new_class)
            self.DB.Session.commit()
            print('创建班级%s-%s成功'%choose_coures.name,class_name)
            res = True
        return res




    def Choose_Student(self):
        '''
        将学员加入到班级
        '''
        table = self.DB.Tables['user']
        type_table = self.DB.Tables['role_type']
        choose_class = self.Sel_Class()
        while True:
            if choose_class is None:
                break
            else:
                print('请选择学生加入你的班级'.center(50,'-'))
                student_list = self.DB.Session.query(table).filter(table.type==self.Get_Role_Type()['student']).all()
                your_student_list = []
                for student in student_list:
                    for course in student.student_courses:
                        if course.course == choose_class.course:
                            your_student_list.append(student)
                if len(your_student_list) ==0:
                    print("还没有学生选择你的课程！")
                    break
                count = 1
                for your_student in your_student_list:
                    print(count,'.',your_student.name,'QQ',your_student.qq)
                    count +=1
                act = input('请选择学生(q推出)：')
                if act.isdigit() and int(act) >0 and int(act) <=len(your_student_list):
                    choose_student = your_student_list[int(act)-1]
                    class_student_table = self.DB.Tables['class_student']
                    in_class = self.DB.Session.query(class_student_table).filter(class_student_table.s_class==choose_class).filter(class_student_table.student==choose_student).all()
                    if len(in_class)==0:
                        add_class_student = class_student_table(s_class=choose_class,student=choose_student)
                        self.DB.Session.add(add_class_student)
                        self.DB.Session.commit()
                        print("添加学员%s成功！"%choose_student.name)
                        continue
                    else:
                        print('学员%s已经存在！'%choose_student.name)
                elif act == 'q':
                    break
                else:
                    print('选择错误!')
                    continue





    def Start_Class(self):
        '''
        开始上课
        :return: 
        '''
        pass

    def Homework_Correcting(self):
        '''
        批改作业
        :return: 
        '''
        pass

###

    def Menu_Student(self):
        '''
        学生接口
        :return: 
        '''
        pass

    def Sel_Student(self):
        '''
        学生选课
        :return: 
        '''
        pass


    def Submit_Homework(self):
        '''
        提交作业
        :return: 
        '''
        pass

    def Show_Score(self):
        '''
        查看成绩
        :return: 
        '''
        pass

#########

    def Open_Homework(self):
        '''
        调用浏览器打开url
        :return: 
        '''
        pass

    def Sel_Class(self):
        '''
        选择班级上课或其他
        :return: 
        '''
        choose = None
        table_course = self.DB.Tables['course']
        table_class = self.DB.Tables['class']
        while True:
            print('选择班级'.center(50,'-'))
            class_obj_list = []
            course_list = self.DB.Session.query(table_course).filter(table_course.teacher == self.Login_User).all()
            for course_obj in course_list:
                temp_class = self.DB.Session.query(table_class).filter(table_class.course==course_obj).all()
                class_obj_list.extend(temp_class)
            count = 1
            if len(class_obj_list) == 0:
                print('你还没创建班级！')
                break
            for class_obj in class_obj_list:
                print(count,'.',class_obj.name,class_obj.course.name)
                count += 1
            act = input("请选择班级：")
            if act.isdigit() and int(act) <= len(class_obj_list) and int(act) >0:
                choose = class_obj_list[int(act)-1]
                break
            else:
                print('选择错误！')
                continue
        return choose






    def Sel_Class_Record(self):
        '''
        选择班级上课记录
        :return: 
        '''
        pass

    def Sel_Course(self):
        '''
        选择班级课程
        :return: 
        '''
        choose = None
        table = self.DB.Tables['course']
        course_list = self.DB.Session.query(table).filter(table.teacher==self.Login_User).all()
        while True:
            print('请选择课程'.center(50,'-'))
            count = 1
            if len(course_list) == 0:
                print('还没有创建课程，请先创建课程!')
                break
            for course_obj in course_list:
                print(count,',',course_obj.name,course_obj.school.name)
                count += 1
            act = input('请选择课程:')
            if act.isdigit() and int(act) <= len(course_list) and int(act) >0:
                choose = course_list[int(act)-1]
                break
            else:
                print("选择错误！")
                continue
        return choose


    def Sel_School(self):
        '''
        选择学校，返回选择的学校ORM
        :return: 
        '''
        choose = None
        school_table = self.DB.Tables['school']
        school_obj = self.DB.Session.query(school_table).all()
        if len(school_obj) == 0:
            print('还未创建学校,请先创建学校！')
            choose = self.Create_School()
        else:
            while True:
                count = 1
                for s_obj in school_obj:
                    print(count,'.',s_obj.name,s_obj.address)
                    count += 1
                act = input('请选择学校:')
                if act.isdigit() and int(act) >0 and int(act) <= len(school_obj):
                    choose = school_obj[int(act)-1]
                    break
                else:
                    print('选择错误！')
                    continue
        return choose

    def Sel_Teacher(self):
        '''
        选择教师，返回教师OBj
        :return: 
        '''
        choose= None
        table = self.DB.Tables['user']
        teacher_list = self.DB.Session.query(table).filter(table.type==self.Get_Role_Type()['teacher']).all()
        if len(teacher_list) == 0:
            print('还未创建老师，请先创建老师！')
            exit()
        while True:
            count = 1
            for teacher_obj in teacher_list:
                print(count,teacher_obj.name)
            act = input('请选择教师：')
            if act.isdigit() and int(act) >0 and int(act) <= len(teacher_list):
                choose = teacher_list[int(act)-1]
                break
            else:
                print('选择错误！')
                continue
        return choose






    def Get_Role_Type(self):
        '''
        返回角色类型字典
        :return: 
        '''
        table = self.DB.Tables['role_type']
        type_obj = self.DB.Session.query(table).all()
        type_dict = {}
        for t in type_obj:
            type_dict[t.name] = t
        return type_dict


