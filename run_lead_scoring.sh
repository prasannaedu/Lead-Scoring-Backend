#!/bin/bash

# -------------------------------
# CONFIGURATION
# -------------------------------
LEADS_FILE="leads.csv"            # Path to your leads CSV
SCORED_FILE="scored_leads.csv"    # Output CSV
OFFER_NAME="Special Discount"
OFFER_VALUE_PROPS=("10% off on all premium products")
OFFER_USE_CASES=("Best for returning customers during holiday season")
API_URL="http://localhost:8000"

# -------------------------------
# UPLOAD LEADS
# -------------------------------
echo "Uploading leads from $LEADS_FILE..."
UPLOAD_RESPONSE=$(curl -s -X POST "$API_URL/leads/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@$LEADS_FILE")

echo "Upload response: $UPLOAD_RESPONSE"

# -------------------------------
# POST OFFER
# -------------------------------
echo "Posting offer..."
OFFER_JSON=$(jq -n \
  --arg name "$OFFER_NAME" \
  --argjson value_props "$(printf '%s\n' "${OFFER_VALUE_PROPS[@]}" | jq -R . | jq -s .)" \
  --argjson ideal_use_cases "$(printf '%s\n' "${OFFER_USE_CASES[@]}" | jq -R . | jq -s .)" \
  '{name:$name,value_props:$value_props,ideal_use_cases:$ideal_use_cases}')

OFFER_RESPONSE=$(curl -s -X POST "$API_URL/offer" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d "$OFFER_JSON")

echo "Offer response: $OFFER_RESPONSE"

# -------------------------------
# SCORE LEADS
# -------------------------------
echo "Scoring leads..."
SCORE_RESPONSE=$(curl -s -X POST "$API_URL/score" -H "accept: application/json")
echo "Score response: $SCORE_RESPONSE"

# -------------------------------
# EXPORT SCORED LEADS CSV
# -------------------------------
echo "Exporting scored leads to $SCORED_FILE..."
curl -s -X GET "$API_URL/export_csv" -H "accept: text/csv" -o "$SCORED_FILE"
echo "Done! Scored leads saved in $SCORED_FILE."
