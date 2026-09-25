/* SPDX-License-Identifier: GPL-3.0-or-later */
#include "windowing/gbm/GBMUtils.h"
#include <cassert>
#include <cstdint>
#include <set>
#include <iostream>

static uintptr_t nextId = 1;
static bool failLock;
static bool freeBuffers = true;
static std::set<gbm_bo*> locked;
extern "C" gbm_bo* gbm_surface_lock_front_buffer(gbm_surface*)
{
  if (failLock)
    return nullptr;
  auto* bo = reinterpret_cast<gbm_bo*>(nextId++);
  assert(locked.insert(bo).second);
  return bo;
}
extern "C" void gbm_surface_release_buffer(gbm_surface*, gbm_bo* bo)
{
  assert(locked.erase(bo) == 1);
}

extern "C" int gbm_surface_has_free_buffers(gbm_surface*)
{
  return freeBuffers;
}

int main()
{
  using Surface = KODI::WINDOWING::GBM::CGBMUtils::CGBMDevice::CGBMSurface;
  {
    Surface surface(reinterpret_cast<gbm_surface*>(1));
    auto* first = surface.LockTransactionalBuffer();
    assert(first && locked.count(first));
    assert(!surface.LockTransactionalBuffer());
    surface.CompleteTransactionalBuffer(true);
    assert(locked.count(first));
    auto* rejected = surface.LockTransactionalBuffer();
    assert(rejected && locked.size() == 2);
    surface.CompleteTransactionalBuffer(false);
    assert(locked.size() == 1 && locked.count(first));
    failLock = true;
    assert(!surface.LockTransactionalBuffer());
    surface.CompleteTransactionalBuffer(true);
    assert(locked.size() == 1 && locked.count(first));
    failLock = false;
    auto* second = surface.LockTransactionalBuffer();
    surface.CompleteTransactionalBuffer(true);
    assert(locked.size() == 1 && locked.count(second));
    surface.CompleteTransactionalBuffer(false);
    assert(locked.count(second));
    assert(surface.LockTransactionalBuffer());
  }
  assert(locked.empty());
  {
    Surface surface(reinterpret_cast<gbm_surface*>(1));
    surface.LockFrontBuffer();
    surface.LockFrontBuffer();
    surface.LockFrontBuffer();
    assert(locked.size() == 3);
    surface.LockTransactionalBuffer();
    surface.CompleteTransactionalBuffer(false);
    assert(locked.size() == 3);
    auto* dv = surface.LockTransactionalBuffer();
    surface.CompleteTransactionalBuffer(true);
    assert(locked.size() == 1 && locked.count(dv));
    auto* restored = surface.LockTransactionalBuffer();
    surface.CompleteTransactionalBuffer(true);
    surface.EndTransactionalMode();
    assert(locked.size() == 1 && locked.count(restored));
    freeBuffers = false;
    auto* normal = surface.LockFrontBuffer().Get();
    assert(locked.size() == 1 && locked.count(normal) && !locked.count(restored));
  }
  assert(locked.empty());
  std::cout << "PASS: actual Kodi GBM owner retains scanout on failed atomic presentation\n";
}
