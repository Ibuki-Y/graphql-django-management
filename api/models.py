from django.db import models


# Departmentモデル
class Department(models.Model):
    # 最大文字数
    dept_name = models.CharField(max_length=50)

    # object返値
    def __str__(self):
        return self.dept_name


# Employeeモデル
class Employee(models.Model):
    name = models.CharField(max_length=50)
    # 入社年度(整数値)
    join_year = models.IntegerField()
    # ForeignKey: 一対多, related_name:逆参照, CASCADE: departmentが削除されると自動削除, blank: 空欄
    department = models.ForeignKey(Department, related_name="employees", on_delete=models.CASCADE, blank=True,
                                   null=True)

    def __str__(self):
        return self.name
