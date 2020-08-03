from rest_framework import status
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from tracker.models import Conversion
from ..permissions import IsSuperUser
from offer.models import Currency


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = (
            'code',
            'name',
        )


class ConversionSerializer(serializers.ModelSerializer):
    currency = CurrencySerializer()

    class Meta:
        model = Conversion
        fields = (
            'id',  # TODO .hex
            'created_at',
            'offer_id',
            'affiliate_id',
            # TODO offer.name
            'revenue',
            'payout',
            'currency',
            'sub1',
            'sub2',
            'sub3',
            'sub4',
            'sub5',
            'status',
            'goal',
            'goal_value',
            'country',
            'ip',
            'ua',
        )


class ConversionCreateView(APIView):
    permission_classes = (IsAuthenticated, IsSuperUser,)

    def post(self, request):
        offer_id = request.data.get('offer_id')
        if not offer_id:
            return Response(
                "Required 'offer_id'",
                status.HTTP_400_BAD_REQUEST
            )
        affiliate_id = request.data.get('pid')
        if not affiliate_id:
            return Response(
                "Required 'pid'",
                status.HTTP_400_BAD_REQUEST
            )
        currency_code = request.data.get('currency')
        currency = None
        if currency_code:
            currency = Currency.objects.filter(code=currency_code).first()

        conversion = Conversion()
        conversion.offer_id = offer_id
        conversion.affiliate_id = affiliate_id
        if request.data.get('goal'):
            conversion.goal_value = request.data.get('goal')
        if request.data.get('revenue'):
            conversion.revenue = request.data.get('revenue')
        if request.data.get('payout'):
            conversion.payout = request.data.get('payout')
        if currency:
            conversion.currency = currency
        conversion.save()

        return Response(
            ConversionSerializer(conversion).data,
            status=status.HTTP_201_CREATED
        )