import graphene

from apps.decks.models import Deck
from apps.cards.models import Card

from apps.decks.schema import CreateDeck, DeckType
from apps.cards.schema import CreateCard, UpdateCard, CardType


class Mutation(graphene.ObjectType):
    create_card = CreateCard.Field()
    create_deck = CreateDeck.Field()

    update_card = UpdateCard.Field()


class Query(graphene.ObjectType):
    decks = graphene.List(DeckType)
    deck_by_id = graphene.List(DeckType, id=graphene.Int())
    deck_cards = graphene.List(CardType, deck=graphene.Int())

    cards = graphene.List(CardType)
    card_by_id = graphene.List(CardType, id=graphene.Int())

    def resolve_decks(self, info):
        return Deck.objects.all()

    def resolve_cards(self, info):
        return Card.objects.all()

    def resolve_deck_cards(self, info, deck):
        return Card.objects.filter(deck=deck)

    def resolve_deck_by_id(self, info, id):
        return Deck.objects.filter(pk=id)

    def resolve_card_by_id(self, info, id):
        return Card.objects.filter(pk=id)


schema = graphene.Schema(query=Query, mutation=Mutation)
