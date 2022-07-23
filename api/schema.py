import graphene
from graphene_django.types import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphene import relay
from graphql_relay import from_global_id
from graphql_jwt.decorators import login_required
from .models import Employee, Department


# Department node
class DepartmentNode(DjangoObjectType):
    class Meta:
        model = Department
        filter_fields = {
            # 逆参照
            'employees': ['exact'],
            'dept_name': ['exact']
        }
        interfaces = (relay.Node,)


# Employee node
class EmployeeNode(DjangoObjectType):
    # nodeにEmployeeモデルを関連付け
    class Meta:
        model = Employee
        # カスタムフィルター
        filter_fields = {
            # exact: 完全一致, icontains: キーワードが含まれるか
            'name': ['exact', 'icontains'],
            'join_year': ['exact', 'icontains'],
            'department__dept_name': ['icontains'],
        }
        # relay node
        interfaces = (relay.Node,)


# Department作成(Mutation)
class DeptCreateMutation(relay.ClientIDMutation):
    class Input:
        dept_name = graphene.String(required=True)

    # インスタンス
    department = graphene.Field(DepartmentNode)

    @login_required
    def mutate_and_get_payload(root, info, **input):
        department = Department(
            dept_name=input.get('dept_name')
        )
        # DBに登録
        department.save()
        # 作成されたdepartmentを返す
        return DeptCreateMutation(department=department)


# Department削除(Mutation)
class DeptDeleteMutation(relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    department = graphene.Field(DepartmentNode)

    @login_required
    def mutate_and_get_payload(root, info, **input):
        department = Department(
            id=from_global_id(input.get('id'))[1]
        )
        # 削除
        department.delete()
        # 空のdepartmentを返す
        return DeptDeleteMutation(department=None)


# Employee作成(Mutation)
class EmployeeCreateMutation(relay.ClientIDMutation):
    class Input:
        name = graphene.String(required=True)
        join_year = graphene.Int(required=True)
        department = graphene.ID(required=True)

    employee = graphene.Field(EmployeeNode)

    @login_required
    def mutate_and_get_payload(root, info, **input):
        employee = Employee(
            name=input.get('name'),
            join_year=input.get('join_year'),
            department_id=from_global_id(input.get('department'))[1]
        )
        employee.save()
        # 作成されたemployeeを返す
        return EmployeeCreateMutation(employee=employee)


# Employee更新(Mutation)
class EmployeeUpdateMutation(relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        name = graphene.String(required=True)
        join_year = graphene.Int(required=True)
        department = graphene.ID(required=True)

    employee = graphene.Field(EmployeeNode)

    @login_required
    def mutate_and_get_payload(root, info, **input):
        employee = Employee(
            id=from_global_id(input.get('id'))[1]
        )
        # input情報に更新
        employee.name = input.get('name')
        employee.join_year = input.get('join_year')
        employee.department_id = from_global_id(input.get('department'))[1]
        employee.save()
        return EmployeeUpdateMutation(employee=employee)


# Employee削除(Mutation)
class EmployeeDeleteMutation(relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    employee = graphene.Field(EmployeeNode)

    @login_required
    def mutate_and_get_payload(root, info, **input):
        employee = Employee(
            id=from_global_id(input.get('id'))[1]
        )
        employee.delete()
        return EmployeeDeleteMutation(employee=None)


class Mutation(graphene.AbstractType):
    create_dept = DeptCreateMutation.Field()
    delete_dept = DeptDeleteMutation.Field()
    create_employee = EmployeeCreateMutation.Field()
    update_employee = EmployeeUpdateMutation.Field()
    delete_employee = EmployeeDeleteMutation.Field()


class Query(graphene.ObjectType):
    # idでemployeeを特定
    employee = graphene.Field(EmployeeNode, id=graphene.NonNull(graphene.ID))
    # employee一覧取得 & filter適応
    all_employees = DjangoFilterConnectionField(EmployeeNode)
    # idでdepartmentを特定
    department = graphene.Field(DepartmentNode, id=graphene.NonNull(graphene.ID))
    # department一覧取得 & filter適応
    all_departments = DjangoFilterConnectionField(DepartmentNode)

    # employee(Query), @login_required: JWT認証(認証してない人に実行させないため)
    @login_required
    def resolve_employee(self, info, **kwargs):
        id = kwargs.get('id')
        if id is not None:
            # idが存在するとき該当するEmployeeを返す
            # from_global_id: 引数の'id'は文字列=>整数変換
            return Employee.objects.get(id=from_global_id(id)[1])

    # all_employees(Query)
    @login_required
    def resolve_all_employees(self, info, **kwargs):
        return Employee.objects.all()

    # department(Query),
    @login_required
    def resolve_department(self, info, **kwargs):
        id = kwargs.get('id')
        if id is not None:
            return Department.objects.get(id=from_global_id(id)[1])

    # all_departments(Query)
    @login_required
    def resolve_all_departments(self, info, **kwargs):
        return Department.objects.all()
