#!/usr/bin/env python

import json
import jwt
from jwt.algorithms import RSAAlgorithm
import os
import requests
from urllib.parse import urlparse


ALLOWED_ISSUERS = os.environ.get('ALLOWED_ISSUERS').split()


def handler(event, context):
    print(f"EVENT:: {event}")
    print(f"CONTEXT:: {context}")
    whole_auth_token = event.get('authorizationToken')
    if not whole_auth_token:
        raise Exception('Unauthorized')

    # auth_header_parts = [x for x in whole_auth_token.split(' ') if x]
    # token_method = auth_header_parts[0]
    # auth_token = auth_header_parts[1]

    token_method, auth_token = whole_auth_token.split(' ')
    print(f"TOKEN-HEADER: {token_method}")
    print(f"AUTH-TOKEN: {auth_token}")

    if not (token_method.lower() == 'bearer' and auth_token):
        print("Failing due to invalid token_method or missing auth_token")
        raise Exception('Unauthorized')

    # We only allow specific issuers
    auth_token_decoded = jwt.decode(auth_token, verify=False)
    iss = auth_token_decoded['iss']
    print(f"ISS: {iss}")
    iss_netloc = urlparse(iss).netloc
    print(f"ISS-NETLOC: {iss_netloc}")
    if iss_netloc not in ALLOWED_ISSUERS:
        print('Failing due to invalid issuer: {}'.format(iss))
        raise Exception('Unauthorized')

    # Issuer is ok. Get the issuers public signing key
    public_key = get_public_key(iss)

    try:
        principal_id = jwt_verify(auth_token, public_key)
        policy = generate_policy(principal_id, 'Allow', event['methodArn'])
        print('Return policy: {}'.format(policy))
        print(f"GENERATED-POLICY: {json.dumps({policy})}")
        return policy
    except Exception as e:
        print(f'Exception encountered: {e}')
        raise Exception('Unauthorized')


def get_public_key(iss):
    #os.environ['NO_PROXY'] = '127.0.0.1,localhost'
    try:
      response = requests.get(f"{iss}/.well-known/openid-configuration")
    except Exception as ex:
      print(ex)
      raise Exception(f"Could not get the well known endpoint for: {iss}")
    jwks_uri = response.json()['jwks_uri']
    response = requests.get(jwks_uri)
    public_key = response.json()['keys'][0]
    return json.dumps(public_key)


def jwt_verify(auth_token, public_key):
    public_key = RSAAlgorithm.from_jwk(public_key)
    decoded = jwt.decode(auth_token, public_key, algorithms='RS256')
    return decoded['sub']


def generate_policy(principal_id, effect, resource):
    return {
        'principalId': principal_id,
        'policyDocument': {
            'Version': '2012-10-17',
            'Statement': [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": effect,
                    "Resource": resource

                }
            ]
        }
    }
