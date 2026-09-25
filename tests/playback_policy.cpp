/* SPDX-License-Identifier: GPL-2.0-or-later */
#include "cores/VideoPlayer/DVDCodecs/Video/DVPlaybackPolicy.h"
#include "cores/VideoPlayer/DVDCodecs/Video/DVPlaybackInfo.h"
#include <cassert>
#include <iostream>

int main()
{
  for (unsigned bits = 0; bits < 64; ++bits)
  {
    // Automatic only for progressive, non-stereo DV on a supported TV/transport.
    assert(DVBRIDGE::Eligible(bits & 1, bits & 2, bits & 4,
                             bits & 8, bits & 16, bits & 32) == (bits == 7));
  }
  for (const auto* source : {"", "5", "7", "8.1", "8.4", "10", "7 FEL"})
  {
    for (unsigned inactive : {0u, 2u, 4u, 6u})
      assert(CDVPlaybackInfo::Detail(source, inactive) == source);
  }
  assert(CDVPlaybackInfo::Detail("7", 7) == "7 FEL · CM4 · HDMI DV");
  assert(CDVPlaybackInfo::Detail("7 FEL", 7) == "7 FEL · CM4 · HDMI DV");
  assert(CDVPlaybackInfo::Detail("8.1", 1) == "8.1 · CM2.9 · HDMI DV");
  assert(CDVPlaybackInfo::Detail("7", 1).find("MEL") == std::string::npos);
  std::cout << "64 automatic routing cases, 28 native labels and 4 active DV labels passed\n";
}
