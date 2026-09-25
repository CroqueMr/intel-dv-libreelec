/* SPDX-License-Identifier: GPL-3.0-or-later */
#pragma once
#include <cerrno>
#include <cstring>
enum { LOGERROR, LOGDEBUG, LOGWARNING, LOGWINDOWING };
struct CLog
{
  template<class... T> static void Log(int, const char*, T&&...) {}
  template<class... T> static void LogF(int, const char*, T&&...) {}
};
