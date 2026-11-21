# FairFarm design system

## Brand direction

FairFarm is calm, practical, and confident: near-black text on an off-white
canvas, white cards, one lime accent, and clear freshness labels. The interface
prioritizes the net amount a farmer takes home rather than raw market price.

## Tokens

The canonical token source is [tokens.json](design/tokens.json). Web CSS
variables in `apps/web/src/styles/tokens.css` and the future Android Compose
theme must mirror it.

- Display: 48px, title: 32px, heading: 24px, body: 16px, caption: 13px.
- Spacing: 4, 8, 16, 24, 32, 48px.
- Cards use a 20px radius; pills use 999px.
- Latin uses Inter; Marathi and Hindi use Noto Sans Devanagari.

## Components and states

- **Primary button:** ink background, white label, lime circular arrow affordance.
- **Secondary button:** white surface, ink border, same minimum touch target.
- **Card:** white surface, soft line border, 20px radius, clear heading and
  supporting value.
- **Freshness badge:** icon plus `FRESH`, `STALE`, `OLD`, or `NO_REPORT`;
  never color alone.
- **Mandi pin:** green/amber/red icon plus a text label in the adjacent legend.
- **Chart:** labels and tooltips expose exact values; color is supported by
  legends and text.
- Loading uses skeleton blocks; empty states explain the next action; errors
  include retry; offline states show the last update time.

## Accessibility and localization

All interactive controls have a 48px/48dp minimum target and visible focus
states. Text and icons meet AA contrast. No meaning is conveyed by color alone.
Every user-facing string is keyed in English, Marathi, and Hindi. Currency is
INR and display amounts are whole rupees rounded half-up; quantities are
quintals.

## Motion

Use short 150–220ms ease-out transitions for cards, tabs, and loading changes.
Respect reduced-motion preferences. No animation is required to understand a
ranking or alert.

## Screen inventory

### Web

Login; Overview; Price Explorer; Regions; Insights; Data; Settings; Query log.

### Android

Language select; Home; Result; Mandi detail; Insights; Ask; Settings.
Bottom navigation is Home, Insights, Ask, Settings.

