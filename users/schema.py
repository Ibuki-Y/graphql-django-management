from django.contrib.auth import get_user_model
import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
import graphql_jwt
from graphql_jwt.decorators import login_required


# User node作成
class UserNode(DjangoObjectType):
    class Meta:
        # django標準モデル
        model = get_user_model()
        filter_fields = {
            'username': ['exact', 'icontains']
        }
        interfaces = (relay.Node,)


# user作成(Mutation)
class UserCreateMutation(relay.ClientIDMutation):
    class Input:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        email = graphene.String(required=True)

    # インスタンス
    user = graphene.Field(UserNode)

    # JWTトークンがないのでlogin_requiredなし
    def mutate_and_get_payload(root, info, **input):
        user = get_user_model()(
            username=input.get('username'),
            email=input.get('email')
        )
        user.set_password(input.get('password'))
        user.save()

        return UserCreateMutation(user=user)


class Mutation(graphene.AbstractType):
    create_user = UserCreateMutation.Field()
    # JWTトークン取得
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()


class Query(graphene.ObjectType):
    # user一覧取得 & filter適応
    all_users = DjangoFilterConnectionField(UserNode)

    @login_required
    def resolve_all_users(self, info, **kwargs):
        #  userのobjectを全て返す
        return get_user_model().objects.all()
