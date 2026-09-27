# SLO: payment-api availability

- Service: payment-api
- SLI: availability — numerator: count of HTTP 2xx/3xx responses served to end users; denominator: total valid requests received.
- target: 99.9%
- window: 28 days
- Owner: payments-team
- Error budget policy: when the remaining error budget drops below 25%, freeze non-essential releases until the budget recovers above 50%.
