import graphene

from datetime import timedelta
from django.utils import timezone

from graphene_django import DjangoObjectType
from graphql import GraphQLError

from .models import Card
from apps.decks.models import Deck


buckets = (
    (1, 1),
    (2, 3),
    (3, 7),
    (4, 1),
    (5, 3)
)


class CardType(DjangoObjectType):
    class Meta:
        model = Card


class CreateCard(graphene.Mutation):
    card = graphene.Field(Card)

    class Arguments:
        question = graphene.String()
        answer = graphene.String()
        deck_id = graphene.Int()

    def mutate(self, info, question, answer, deck_id):
        card = Card(question=question, answer=answer, deck_id=deck_id)
        deck = Deck.objects.get(id=deck_id)
        card.deck = deck
        card.save()
        return CreateCard(card=card)


class UpdateCard(graphene.Mutation):
    card = graphene.Field(Card)

    class Arguments:
        id = graphene.ID()
        question = graphene.String()
        answer = graphene.String()
        status = graphene.Int(description="easy, average, or difficult -> 1, 2, 3")

    def mutate(self, info, id, question, answer, status):
        if status not in [1, 2, 3]:
            raise GraphQLError('Invalid Status. must be 1, 2 or 3')

        card = Card.objects.get(pk=id)
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

