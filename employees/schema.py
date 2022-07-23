import graphene
import api.schema
import users.schema


# apiとusersのQueryを合成
class Query(users.schema.Query, api.schema.Query, graphene.ObjectType):
    pass


# apiとusersのMutationを合成
class Mutation(users.schema.Mutation, api.schema.Mutation, graphene.ObjectType):
    pass


# employees/setting.pyのGRAPHENE(SCHEMA)で指定
schema = graphene.Schema(query=Query, mutation=Mutation)
