# Search Pitfalls and Mitigations

## Engine-limit pitfalls

1. **SearXNG public instances are unstable**
   - Symptom: intermittent timeouts or empty results
   - Mitigation: implement automatic switching across instances, set reasonable timeouts
   - Recommendation: self-host a SearXNG instance in production

2. **DuckDuckGo anti-scraping**
   - Symptom: after consecutive requests, returns CAPTCHA or empty results
   - Mitigation: request interval ≥ 1 second, use a proxy pool
   - Recommendation: rate-limit; don't call at high frequency

3. **Brave Search quota exhausted**
   - Symptom: returns 403 or empty results
   - Mitigation: monitor quota usage, implement automatic degradation
   - Recommendation: the free quota is enough for personal use

## Result-quality issues

4. **Irrelevant search results**
   - Symptom: returned results are unrelated to the query
   - Mitigation: refine query terms, use quotes for exact match
   - Recommendation: provide multiple alternative queries

5. **Stale results**
   - Symptom: returned content is outdated or links are dead
   - Mitigation: check result dates, prefer recent content
   - Recommendation: label the result publication date

6. **Duplicate results**
   - Symptom: the same content appears in multiple results
   - Mitigation: dedupe by URL, merge similar results
   - Recommendation: set a dedup threshold

## Cache pitfalls

7. **Cache pollution**
   - Symptom: a wrong result is cached, and all subsequent requests return the wrong thing
   - Mitigation: validate result validity before caching
   - Recommendation: set a cache TTL, auto-expire on expiry

8. **Cache breakdown**
   - Symptom: hot queries cause frequent cache invalidation
   - Mitigation: extend the cache time for hot queries
   - Recommendation: implement cache warm-up

## Parsing pitfalls

9. **HTML structure changes**
   - Symptom: the search engine updates its page structure, breaking parsing
   - Mitigation: use robust parsers that support multiple selectors
   - Recommendation: monitor the parse success rate and update promptly

10. **Encoding issues**
    - Symptom: CJK results show garbled text
    - Mitigation: set encoding correctly, use UTF-8
    - Recommendation: detect the encoding and convert automatically

## Security pitfalls

11. **Malicious websites**
    - Symptom: search results include malicious sites
    - Mitigation: filter suspicious domains, flag security risks
    - Recommendation: use a whitelist of safe search engines

12. **Privacy leakage**
    - Symptom: search requests leak user privacy
    - Mitigation: use anonymous engines, don't record search history
    - Recommendation: deploy the search engine locally

## Engineering pitfalls

13. **Resource leaks**
    - Symptom: a large volume of search requests causes a memory leak
    - Mitigation: use a connection pool, release resources promptly
    - Recommendation: monitor memory usage

14. **Circular dependencies**
    - Symptom: the search module is circularly depended on by other modules
    - Mitigation: define module boundaries clearly
    - Recommendation: use dependency injection
