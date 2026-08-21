Candidate notes session 34

Selected candidate: CVE-2023-32439 / WebKit Bug 256567.

Public fix: https://github.com/WebKit/WebKit/commit/52fe95e5805c735cc1fa4d6200fcaa1912efbfea
Commit title: EnumeratorNextUpdateIndexAndMode and HasIndexedProperty should have different heap location kinds.
Author: hyjorc1. Commit date rendered by GitHub: 2023-05-10.
Canonical link: https://commits.webkit.org/263909@main
Bug: https://bugs.webkit.org/show_bug.cgi?id=256567

GitHub commit page states that EnumeratorNextUpdateIndexAndMode and HasIndexedProperty are different DFG nodes but could introduce the same heap location kind in DFGClobberize.h, leading to a hash collision. The fix introduces a new location kind for EnumeratorNextUpdateIndexAndMode and updates DFGHeapLocation.cpp/.h, DFGClobberize.h and DFGInPlaceAbstractState.cpp.

Public regression test shown on the commit page:
JSTests/stress/heap-location-collision-dfg-clobberize.js
It sets a default watchdog, creates arr = [0], loops over `for (let _ in arr)`, performs `0 in arr`, and loops forever. This is a regression/watchdog test, not a payload and not evidence of a native-code primitive by itself.

Sony WebKit-601-1300 public mirror: commit d636699770323d7968a2c37955aa513bda5f8a37.
Relevant paths present in the tree:
- Source/JavaScriptCore/dfg/DFGClobberize.h
- Source/JavaScriptCore/dfg/DFGHeapLocation.cpp
- Source/JavaScriptCore/dfg/DFGHeapLocation.h
- Source/JavaScriptCore/dfg/DFGInPlaceAbstractState.cpp
- Source/JavaScriptCore/runtime/JSArray.cpp
- Source/JavaScriptCore/runtime/ArrayPrototype.cpp
No `EnumeratorNextUpdateIndexAndMode` occurrence was found in the inspected 601-1300 DFGClobberize/heap-location paths before the lazy scan was stopped. `HasIndexedPropertyLoc` is present. This is a structural precondition/correlation point, not proof of a vulnerability in 601 or PS4 13.52.

Important safety/classification boundary: the candidate is a JIT/DFG abstract-heap collision that can cause incorrect compiler reasoning; the public commit and test do not alone prove arbitrary read/write or native usermode. Native usermode requires additional evidence and cannot be claimed from this candidate alone.
