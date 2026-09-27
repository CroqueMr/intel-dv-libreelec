// SPDX-License-Identifier: GPL-2.0-or-later
#include "windowing/gbm/drm/DVBridgeKernelLogReader.h"
#include <cassert>
#include <cstring>
#include <string>

static int opens, reads, closes, phase;
static bool denied, overrun;
static std::string record;
extern "C" int __wrap_open(const char* path, int flags, ...)
{
  ++opens;
  assert(std::strcmp(path, "/dev/kmsg") == 0);
  assert((flags & O_ACCMODE) == O_RDONLY);
  assert((flags & O_NONBLOCK) && (flags & O_CLOEXEC));
  if (denied) { errno = EACCES; return -1; }
  return 4242;
}
extern "C" ssize_t __wrap_read(int fd, void* buffer, size_t capacity)
{
  assert(fd == 4242);
  ++reads;
  if (overrun || phase++ == 0) { errno = EPIPE; return -1; }
  if (phase == 2)
  {
    assert(record.size() <= capacity);
    std::memcpy(buffer, record.data(), record.size());
    return record.size();
  }
  errno = EAGAIN;
  return -1;
}
extern "C" int __wrap_close(int fd)
{
  assert(fd == 4242);
  ++closes;
  return 0;
}
// Fortified builds may route read() through the checked libc entry point.
extern "C" ssize_t __wrap___read_chk(int fd, void* buffer, size_t count, size_t capacity)
{
  assert(count <= capacity);
  return __wrap_read(fd, buffer, count);
}
int main()
{
  timespec now{};
  clock_gettime(CLOCK_MONOTONIC, &now);
  const auto us = uint64_t(now.tv_sec) * 1000000 + now.tv_nsec / 1000;
  record = "3,1," + std::to_string(us) + ",-;DVBridge: link rejected errno=-95\n";
  {
    DVBRIDGE::KernelLogReader reader;
    reader.Collect();
    assert(opens == 1 && reads == 3); // EPIPE recovery, record, EAGAIN.
    reader.Collect();
    assert(opens == 1 && reads == 4); // Retains independent kernel cursor.
    overrun = true;
    const auto before = reads;
    reader.Collect();
    assert(reads - before <= 4096); // Persistent errors cannot loop forever.
  }
  assert(closes == 1);
  denied = true;
  const auto before = reads;
  { DVBRIDGE::KernelLogReader reader; reader.Collect(); }
  assert(reads == before && closes == 1); // No reads/invalid closes after denial.
}
