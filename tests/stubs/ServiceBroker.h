/* SPDX-License-Identifier: GPL-3.0-or-later */
#pragma once
struct CApplicationPlayer { bool HasVisibleOverlay() const { return false; } };
struct TestWindowManager { bool HasVisibleControls() const { return false; } };
struct TestGUI { TestWindowManager& GetWindowManager() { static TestWindowManager v; return v; } };
struct TestLogging { bool CanLogComponent(int) const { return false; } };
struct TestComponents
{
  template<class T> T* GetComponent() { static T value; return &value; }
};
struct CServiceBroker
{
  static TestGUI* GetGUI() { static TestGUI v; return &v; }
  static TestLogging& GetLogging() { static TestLogging v; return v; }
  static TestComponents& GetAppComponents() { static TestComponents v; return v; }
};
