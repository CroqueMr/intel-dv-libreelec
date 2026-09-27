/* SPDX-License-Identifier: GPL-2.0-or-later */
#include "utils/DVBridgeDiagnosticState.h"
#include <cassert>

int main()
{
  DVBRIDGE::DiagnosticFailures state;
  assert(state.Count() == 0);
  assert(state.Record(100));
  for (unsigned i = 101; i < 5100; ++i)
    assert(!state.Record(i));
  assert(state.Record(5100));
  assert(state.Count() == 5001);
  state.Reset();
  assert(state.Count() == 0);
  assert(state.Record(5101));
  assert(!state.Record(5102));
}
