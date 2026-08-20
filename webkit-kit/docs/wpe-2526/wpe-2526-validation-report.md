# WPE WebKit 2.52.6 headless smoke report

> This report records only explicit runner output. A host/offscreen PASS is not a WPE/WebCore PASS.

| Field | Value |
|---|---|
| Runner status | **PASS** |
| Comparison status | **PASS** |
| Reason | all expected stages and capabilities matched |
| Runtime | `WPE MiniBrowser WebDriver` |
| Binary SHA-256 | `NOT_RUN` |
| Architecture probe | `NOT_RUN` |
| Process elapsed | `NOT_RUN` seconds |

## Fixture validation

| Fixture | SHA-256 | Status |
|---|---|---|
| page1 | `3854930be7753028e3800233758f7015f5f2be590fe3663f0fb61ab035f36e7b` | **PASS** |
| page2 | `66b593648c6cec245b505cad043d75a2c2c32d9c2ef0092b203fa17f500dd399` | **PASS** |
| page3 | `5993bffdc8ff066c281f6786088abae42fd3e6900ee6c3cc86804774bd84ee87` | **PASS** |

## Capability comparison

| Capability | Status | Stages |
|---|---|---|
| animation | **PASS** | page1 |
| canvas | **PASS** | page1 |
| css | **PASS** | page1 |
| dom | **PASS** | page1, page2, page3 |
| events | **PASS** | page1, page2 |
| flex | **PASS** | page1 |
| forms | **PASS** | page1 |
| grid | **PASS** | page1 |
| history | **PASS** | page3 |
| images | **PASS** | page1 |
| javascript | **PASS** | page1, page2, page3 |
| localstorage | **PASS** | page1, page2 |
| navigation | **PASS** | page2, page3 |
| svg | **PASS** | page1 |
| text | **PASS** | page1 |

## Runtime evidence

```json
{
  "process": {},
  "runtime": {
    "description": "WPE MiniBrowser WebDriver"
  }
}
```
