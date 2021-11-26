from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_204_NO_CONTENT, HTTP_403_FORBIDDEN
from django.contrib.auth.models import User
# Create your views here.
from .models import User, Chaves

from .serializers import ProfileSerializer, ChavesSerializer
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .permissions import IsUserPermission, IsChavesPermission
import requests

class ProfileView(APIView):
    permission_classes = (AllowAny,IsUserPermission)
    def get(self, request, *args, **kwargs):

        queryset = User.objects.filter(email=request.user) #get the profile of logged in user
        serializer = ProfileSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):

        serializer = ProfileSerializer(data=request.data)
        if serializer.is_valid():
            if request.user.is_anonymous == True:  #If user isn't admin don't allow them to change staff or admin
                serializer.validated_data["staff"] = False
                serializer.validated_data["admin"] = False
                instance = serializer.save()
                instance.set_password(instance.password)
                instance.save()
                return Response(serializer.data, status=HTTP_201_CREATED)
            elif request.user.is_admin == False:
                serializer.validated_data["staff"] = False
                serializer.validated_data["admin"] = False
                instance = serializer.save()
                instance.set_password(instance.password)
                instance.save()
                return Response(serializer.data, status=HTTP_201_CREATED)
            else:
                instance = serializer.save()
                instance.set_password(instance.password)
                instance.save()
                return Response(serializer.data, status=HTTP_201_CREATED)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


    def put(self, request, *args, **kwargs):
        try:
            profile = User.objects.get(email=request.user)
            serializer = ProfileSerializer(profile, data=request.data)
            if serializer.is_valid():
                if request.user.is_admin == False:
                    serializer.validated_data["staff"] = False
                    serializer.validated_data["admin"] = False
                    instance = serializer.save()
                    instance.set_password(instance.password)
                    instance.save()
                    return Response(serializer.data)
                else:
                    instance = serializer.save()
                    instance.set_password(instance.password)
                    instance.save()
                    return Response(serializer.data)
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
        except:
            return Response(status=HTTP_403_FORBIDDEN)

    def delete(self, request, *args, **kwargs):
        try:
            profile = User.objects.get(email=request.user)
            profile.delete()
            return Response(status=HTTP_204_NO_CONTENT)
        except:
            return Response(status=HTTP_403_FORBIDDEN)


class ChavesView(APIView):
    permission_classes = (IsAuthenticated,IsChavesPermission)
    def get(self, request, *args, **kwargs):

        queryset = Chaves.objects.filter(fkuser=request.user)
        serializer = ChavesSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = ChavesSerializer(data=request.data)

        if serializer.is_valid():
            if serializer.validated_data["fkuser"] == request.user:
                serializer.save()
                return Response(serializer.data, status=HTTP_201_CREATED)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


    def put(self, request, *args, **kwargs):
        #print(request.data)
        atualizar = Chaves.objects.get(fkuser=request.user, id=request.data["id"])
        serializer = ChavesSerializer(atualizar, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        deletartudo = Chaves.objects.filter(fkuser=request.user)

        deletartudo.delete()
        return Response(status=HTTP_204_NO_CONTENT)
        
class ChavesDetailView(APIView):
    permission_classes = (IsAuthenticated, IsChavesPermission)

    def get(self, request, *args, **kwargs):
        #print(Chaves.objects.values())
        queryset = Chaves.objects.filter(fkuser=request.user, id=self.kwargs.get('pk'))
        serializer = ChavesSerializer(queryset, many=True)
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        deletarunico = Chaves.objects.filter(fkuser=request.user, id=self.kwargs.get('pk'))
        #print(deletartudo)
        deletarunico.delete()
        return Response(status=HTTP_204_NO_CONTENT)

class BitqueryView(APIView):
    permission_classes = (IsAuthenticated, IsChavesPermission)



    def get(self, request, *args, **kwargs):
        def run_query(query, variables):  # A simple function to use requests.post to make the API call.
            headers = {'X-API-KEY': 'BQYRJvVXxFdjJ4Lw5JuZh8YahPXT3tJ5'}
            request = requests.post('https://graphql.bitquery.io/',
                                    json={'query': query, "variables": variables}, headers=headers)
            if request.status_code == 200:
                return request.json()
            else:
                raise Exception('Query failed and return code is {}.      {}'.format(request.status_code,
                                                                                     query))


        query = """query($network: EthereumNetwork!, $exchange: String!, $baseCurrency: String!, $quoteCurrency: String!, $dia: Boolean!, $hora: Boolean!, $minuto: Boolean!) {
                      ethereum(network: $network) {
                        dexTrades(
                          exchangeName: {is: $exchange}
                          baseCurrency: {is: $baseCurrency}
                          quoteCurrency: {is: $quoteCurrency}
                          
                        ) {
                          timeInterval @include(if: $dia){
                            day(count: 1) 
                          }
                          timeInterval @include(if: $hora){
                            hour(count: 1) 
                          }
                          timeInterval @include(if: $minuto){
                            minute(count: 1) 
                          }
                          baseCurrency {
                            symbol
                            address
                          }
                          baseAmount
                          quoteCurrency {
                            symbol
                            address
                          }
                          quoteAmount
                          trades: count
                          quotePrice
                          maximum_price: quotePrice(calculate: maximum)
                          minimum_price: quotePrice(calculate: minimum)
                          open_price: minimum(of: block, get: quote_price)
                          close_price: maximum(of: block, get: quote_price)
                        }
                      }
                    }"""
        rede = self.kwargs.get('rede')
        exchange = self.kwargs.get('exchange')
        contrato = self.kwargs.get('contrato')
        contratopar = self.kwargs.get('contratopar')
        timeframe = self.kwargs.get('timeframe')
        if timeframe == "day":
            dia = True
            hora = False
            minuto = False
        elif timeframe == "hour":
            dia = False
            hora = True
            minuto = False
        elif timeframe == "minute":
            dia = False
            hora = False
            minuto = True
        count = self.kwargs.get('count')

        variables = {
            "network": rede,
            "exchange": exchange,
            "baseCurrency": contrato,
            "quoteCurrency": contratopar,
            "timeInterval": timeframe,
            "dia": dia,
            "hora": hora,
            "minuto": minuto,

            #"count": count,

        }
        print(variables)
        resultado = run_query(query, variables)
        print(resultado)
        return Response(resultado)



        #print(self.kwargs.get('exchange'))
        #return Response(self.kwargs.get('exchange'))