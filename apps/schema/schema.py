import graphene

from datetime import timedelta
from django.utils import timezone

from graphene_django import DjangoObjectType

from apps.decks.models import Deck as DeckModel
from apps.cards.models import Card as CardModel

buckets = (
    (1, 1),
    (2, 3),
    (3, 7),
    (4, 1),
    (5, 3)
)


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


class UpdateCard(graphene.Mutation):
    card = graphene.Field(Card)

    class Arguments:
        id = graphene.ID()
        question = graphene.String()
        answer = graphene.String()
        status = graphene.Int()

    def mutate(self, info, id, question, answer, status):
        card = CardModel.objects.get(pk=id)
        bucket = card.bucket

        if status == 1 and bucket > 1:
            bucket -= 1
        elif status == 3 and bucket <= 4:
            bucket += 1

        days = buckets[bucket-1][1]
        next_review_at = timezone.now() + timedelta(days=days)

        card.question = question
        card.answer = answer
        card.bucket = bucket
        card.next_review_at = next_review_at
        card.last_review_at = timezone.now()
        card.save()
        return UpdateCard(card=card)


class Mutation(graphene.ObjectType):
    create_card = CreateCard.Field()
    create_deck = CreateDeck.Field()

    update_card = UpdateCard.Field()


class Query(graphene.ObjectType):
    decks = graphene.List(Deck)
    deck_by_id = graphene.List(Deck, id=graphene.Int())
    deck_cards = graphene.List(Card, deck=graphene.Int())

    cards = graphene.List(Card)
    card_by_id = graphene.List(Card, id=graphene.Int())

    def resolve_decks(self, info):
        return DeckModel.objects.all()

    def resolve_cards(self, info):
        return CardModel.objects.all()

    def resolve_deck_cards(self, info, deck):
        return CardModel.objects.filter(deck=deck)

    def resolve_deck_by_id(self, info, id):
        return DeckModel.objects.filter(pk=id)

    def resolve_card_by_id(self, info, id):
        return CardModel.objects.filter(pk=id)


schema = graphene.Schema(query=Query, mutation=Mutation)
