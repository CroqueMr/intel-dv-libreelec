/* SPDX-License-Identifier: GPL-3.0-or-later */
#pragma once
// Transaction tests do not read the host kernel ring or run background IO.
struct CJobManager
{
  template<class F> void Submit(F) {}
};
