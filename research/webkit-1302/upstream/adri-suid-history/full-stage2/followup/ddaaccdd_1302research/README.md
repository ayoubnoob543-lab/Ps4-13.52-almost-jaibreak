# CSSFontFace-Exploit-1302
Based on: https://github.com/ntfargo/CSSFontFace-Exploit by ntfargo

IT IS NOT A JB. IT IS AN ATTEMPT to adapt ntfargo/CSSFontFace-exploit to 13.02

What works

- UAF trigger: getter FontFace.prototype.then is called, this === A: true ✓
- FontFace B captured before the getter (captured_B, unicodeRange U+42) ✓
- UAF rule index is correct ✓

Fundamental problem:
B is never freed. captured_B.unicodeRange returns even 3+ seconds after any deletion attempts.

All available release vectors have been tried:

- deleteRule in getter — B is alive
- deleteRule
- reflow — B is alive
- fonts.delete in getter — browser crash
- Post-load spray after timeout — B is alive
- Post-load spray after 3 seconds — B is alive
- 404 response to .woff request — B is alive

Conclusion: This specific UAF vector via the FontFaceSet::load thenable getter does not work on 13.02 for architectural reasons, not due to incorrect offsets or timing. To continue, you must either find another UAF vector in 13.02 WebKit (requires the libSceWebKit2.sprx binary from 13.02 for reversal) or wait for a public exploit.

What's been revealed:

- Confirmed that the FontFace.prototype.then getter is called on 13.02—this wasn't publicly documented.
- Documented behavior of matchingFaces on 13.02: B remains alive indefinitely, which differs from upstream WebKit before the Niwa fix.
- This narrows the search: either Sony backported the protection before upstream, or their implementation of FontFaceSet::load is fundamentally different.
- The code with diagnostics is a real starting point for anyone with a 13.02 binary.

Note:
The code logs "UAF Achieved" after the getter fires, but this is misleading — it only confirms the thenable getter was triggered. True UAF (freed memory reuse via ArrayBuffer spray) was never achieved because B is never actually freed.
if you want to see all the debug logs change 137th line in index.html set the verbose to true
