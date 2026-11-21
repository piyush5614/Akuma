# FairFarm wireframes

These are behavior-first wireframes. The visual preview is in
[preview.html](preview.html).

## Web

```text
LOGIN                 [FairFarm mark] [Language]
                      Email __________
                      Password _______ [Show]
                      [Sign in ----------------]

OVERVIEW              [Sidebar: Overview | Explorer | Regions | Insights | Data | Settings | Queries]
  Good morning        [Fresh reports] [Searches] [Avg net gain]
  [Crop selector] [Date] [Top mandis ranked by net return]
  [Map / pin legend] [Recent query activity]

PRICE EXPLORER        [Crop] [Location] [Radius] [Search]
  [Map with labeled pins]       [Rank | Mandi | Net/quintal | Freshness]
  [Trend chart]                 [Empty / error / retry state]

REGIONS               [Crop] [Date]
  [District price circles map]  [Region table with freshness labels]

INSIGHTS              [Crop] [Water availability]
  [Seasonality chart + best/worst months]
  [Crop profit range cards + risk factors]
  [Backtest hit rate vs baseline + sample count]

DATA                  [Import CSV] [Validation preview] [Import]
  [Freshness table] [Record type / DEMO label]

SETTINGS              [Road factor] [Transport rate] [Fee] [Shrinkage by crop]
                      [Save changes] [Success/error notice]

QUERY LOG             [Date] [Crop] [Export]
  [Anonymised query table] [Pagination]
```

## Android

```text
LANGUAGE              FairFarm
                      [English] [मराठी] [हिन्दी]
                      [Continue]

HOME                  [Language] [Offline/last updated banner]
                      Crop [picker] Quantity [quintal]
                      Location [Use GPS] [Search manually]
                      [Find best mandi]
                      Bottom: Home | Insights | Ask | Settings

RESULT                [Back] Onion · 10 quintal [Speaker]
                      [BEST NET RETURN ₹22,314] [FRESH]
                      [SELL NOW / WAIT chip] Guidance disclaimer
                      [Ranked mandi cards] [Map toggle]

MANDI DETAIL          [Mandi name] [Freshness]
                      [Trend chart] [Cost breakdown]
                      [Navigate] [Speaker]

INSIGHTS              [Seasonality] [Crop profit]
                      [Chart] [Range cards] [Risk and source labels]

ASK                   [Conversation]
                      [Suggestion chips]
                      [Type message __________] [Mic] [Send] [Speaker]

SETTINGS              Language | Vehicle rate | Water availability
                      About | Data freshness
                      [Save] [Back]
```
