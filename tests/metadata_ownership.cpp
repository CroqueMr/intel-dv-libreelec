/* SPDX-License-Identifier: GPL-2.0-or-later */
#include "DVMetadataBuffer.h"

#include <cassert>
#include <iostream>
#include <vector>

int main()
{
  CDVMetadataBuffer frame;
  assert(!frame.Data() && frame.Size() == 0);
  std::vector<uint8_t> source{1, 2, 3, 4};
  assert(frame.Assign(source.data(), source.size()));
  source[0] = 99;
  assert(frame.Data()[0] == 1);

  CDVMetadataBuffer displayed = frame;
  frame.Reset();
  assert(displayed.Size() == 4 && displayed.Data()[0] == 1);
  assert(!frame.Data());

  assert(frame.Assign(source.data(), source.size()));
  assert(!frame.Assign(nullptr, 4));
  assert(!frame.Data());
  assert(!frame.Assign(source.data(), 0));
  assert(!frame.Assign(source.data(), 1024 * 1024 + 1));

  CDVMetadataBuffer queued;
  queued = displayed;
  displayed.Reset();
  assert(queued.Data()[3] == 4);
  queued = queued;
  assert(queued.Size() == 4);
  assert(queued.Assign(queued.Data(), queued.Size()));
  assert(queued.Data()[3] == 4);
  queued.Reset();
  std::cout << "PASS: metadata ownership, copy lifetime, reset, invalid-size rejection\n";
}
