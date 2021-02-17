import graphene

from graphene_django import DjangoObjectType

from apps.users.models import User as UserModel
from apps.decks.models import Deck as DeckModel
from apps.cards.models import Card as CardModel


class User(DjangoObjectType):
    class Meta:
        model = UserModel


class Deck(DjangoObjectType):
    class Meta:
        model = DeckModel


class CreateDeck(graphene.Mutation):
    deck = graphene.Field(Deck)

    class Arguments:
        title = graphene.String()
        description = graphene.String()

    def mutate(self, info, title, description):
        deck = DeckModel(title=title, description=description)
        deck.save()
        return CreateDeck(deck=deck)


class Card(DjangoObjectType):
    class Meta:
        model = CardModel


class CreateCard(graphene.Mutation):
    card = graphene.Field(Card)

    class Arguments:
        question = graphene.String()
        answer = graphene.String()
        deck_id = graphene.Int()

    def mutate(self, info, question, answer, deck_id):
        card = CardModel(question=question, answer=answer, deck_id=deck_id)
        deck = DeckModel.objects.get(id=deck_id)
        card.deck = deck
        card.save()
        return CreateCard(card=card)


class Mutation(graphene.ObjectType):
    create_card = CreateCard.Field()
    create_deck = CreateDeck.Field()


class Query(graphene.ObjectType):
    users = graphene.List(User)
    decks = graphene.List(Deck)
    cards = graphene.List(Card)
    deck_cards = graphene.List(Card)

    def resolve_users(self, info):
        return UserModel.objects.all()

    def resolve_decks(self, info):
        return DeckModel.objects.all()

    def resolve_cards(self, info):
        return CardModel.objects.all()


schema = graphene.Schema(query=Query, mutation=Mutation)
