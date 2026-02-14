import graphene
import graphql_jwt
from shop.schema import Query as ShopQuery, Mutation as ShopMutation


class Query(ShopQuery, graphene.ObjectType):
    pass


class Mutation(ShopMutation, graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
