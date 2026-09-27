// SPDX-License-Identifier: GPL-2.0-or-later
#include "utils/DVBridgeKernelLog.h"
#include <cassert>
#include <string>

int main()
{
  DVBRIDGE::KernelLogFilter filter;
  assert(!filter.Accept("broken", 20000000));
  assert(!filter.Accept("3,1,1,-;DVBridge: old\n", 20000000));
  assert(!filter.Accept("30,2,19999999,-;DVBridge: userspace injection\n", 20000000));
  assert(!filter.Accept("3,3,19999999,-;unrelated private system message\n", 20000000));
  const auto good = filter.Accept("3,4,19999999,-;i915 0000:00:02.0: DVBridge: link rejected errno=-95\n DEVICE=pci\n", 20000000);
  assert(good && good->find("seq=4") != std::string::npos);
  assert(good->find("errno=-95") != std::string::npos);
  assert(good->find("DEVICE") == std::string::npos);
  assert(!filter.Accept("3,4,19999999,-;DVBridge: duplicate\n", 20000000));
  assert(!filter.Accept("3,3,19999999,-;DVBridge: out of order\n", 20000000));
  assert(!filter.Accept("3,5,20000001,-;DVBridge: future\n", 20000000));
  assert(!filter.Accept("3,18446744073709551616,1,-;DVBridge: overflow\n", 20000000));
  assert(!filter.Accept("3,6,bad,-;DVBridge: invalid timestamp\n", 20000000));
  const auto extended = filter.Accept("3,6,19999999,-,future-field;DVBridge: accepted\n", 20000000);
  assert(extended);
  const auto bounded = filter.Accept("3,7,19999999,-;DVBridge: " + std::string(9000, 'a'), 20000000);
  assert(bounded && bounded->size() < 2110);
}
