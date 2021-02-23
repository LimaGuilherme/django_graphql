import graphene

from graphene_django import DjangoObjectType

from .models import Deck


class DeckType(DjangoObjectType):
    class Meta:
        model = Deck


class CreateDeck(graphene.Mutation):
    deck = graphene.Field(DeckType)

    class Arguments:
        title = graphene.String()
        description = graphene.String()

    def mutate(self, info, title, description):
        deck = Deck(title=title, description=description)
        deck.save()
        return CreateDeck(deck=deck)

