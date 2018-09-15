from datastore import models

from graphene import Node,relay, ObjectType
from graphene_django.types import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
import graphene

class UserNode(DjangoObjectType):
    class Meta:
        model = models.APIUser
        filter_fields = ['id','email']
        interfaces = (relay.Node, )


class ReceiptNode(DjangoObjectType):
    class Meta:
        model = models.Receipt
        filter_fields = ['id','user__email']
        interfaces = (relay.Node, )


class ItemNode(DjangoObjectType):
    class Meta:
        model = models.Item
        filter_fields = ['id','receipt__id','display_name']
        interfaces = (relay.Node, )

class IngredientNode(DjangoObjectType):
    class Meta:
        model = models.ItemIngredient
        filter_fields = ['id','item__id','display_name']
        interfaces = (relay.Node, )

class DatastoreQuery(object):
    receipt = relay.Node.Field(ReceiptNode)
    all_receipts = DjangoFilterConnectionField(ReceiptNode)

    item = relay.Node.Field(ItemNode)
    all_items = DjangoFilterConnectionField(ItemNode)

    ingredient = relay.Node.Field(IngredientNode)
    all_ingredients = DjangoFilterConnectionField(IngredientNode)

    #all_receipts = DjangoFilterConnectionField(ReceiptNode)
    #all_items = graphene.List(ItemType)
    #all_ingredients = graphene.List(IngredientType)

    #def resolve_all_receipts(self, info, **kwargs):
        #return models.Receipt.objects.all()

    #def resolve_all_items(self, info, **kwargs):
        #return models.Item.objects.all()

    #def resolve_all_ingredients(self, info, **kwargs):
        #return models.ItemIngredient.objects.all()

class Query(DatastoreQuery, graphene.ObjectType):
    # This class will inherit from multiple Queries
    # as we begin to add more apps to our project
    pass

schema = graphene.Schema(query=Query)


