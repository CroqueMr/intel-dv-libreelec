/* SPDX-License-Identifier: GPL-3.0-or-later */
#include "windowing/gbm/drm/DRMAtomic.h"
#include "windowing/gbm/drm/DVBridgeState.h"
#include <cassert>
#include <cstdlib>
#include <iostream>
#include <map>
#include <set>

using namespace KODI::WINDOWING::GBM;
static bool rejectTest, rejectCommit, missingProperty;
static int tests, commits, cached;
static bool otherPlane, brokenBlob;
static uint32_t nextBlob = 100;
static std::set<uint32_t> blobs;
static std::map<std::string, uint32_t> ids;
static std::map<uint32_t, uint64_t> staged;
static std::map<std::string, uint64_t> values = {
    {"DVBRIDGE_DV_STANDARD_LAB", 0}, {"HDR_OUTPUT_METADATA", 42},
    {"max bpc", 10}, {"Broadcast RGB", 0}, {"Colorspace", 9},
    {"CTM", 43}, {"GAMMA_LUT", 0}, {"VRR_ENABLED", 1}, {"alpha", 40000}};

extern "C" int drmModeAtomicCommit(int, drmModeAtomicReq*, uint32_t flags, void*)
{
  assert(!(flags & DRM_MODE_ATOMIC_NONBLOCK));
  if (flags & DRM_MODE_ATOMIC_TEST_ONLY)
  {
    ++tests;
    return rejectTest ? -1 : 0;
  }
  ++commits;
  return rejectCommit ? -1 : 0;
}
extern "C" int drmModeCreatePropertyBlob(int, const void*, size_t, uint32_t* id)
{
  *id = ++nextBlob;
  blobs.insert(*id);
  return 0;
}
extern "C" int drmModeDestroyPropertyBlob(int, uint32_t id) { blobs.erase(id); return 0; }
extern "C" drmModePropertyBlobPtr drmModeGetPropertyBlob(int, uint32_t id)
{
  if (brokenBlob)
    return nullptr;
  auto* blob = static_cast<drmModePropertyBlobPtr>(std::calloc(1, sizeof(drmModePropertyBlobRes)));
  blob->id = id;
  blob->length = 8;
  blob->data = std::calloc(1, 8);
  return blob;
}
extern "C" drmModePlaneResPtr drmModeGetPlaneResources(int)
{
  auto* resources = static_cast<drmModePlaneResPtr>(std::calloc(1, sizeof(drmModePlaneRes)));
  resources->count_planes = otherPlane ? 2 : 1;
  resources->planes = static_cast<uint32_t*>(std::calloc(2, sizeof(uint32_t)));
  resources->planes[1] = 8;
  return resources;
}
extern "C" drmModePlanePtr drmModeGetPlane(int, uint32_t id)
{
  auto* plane = static_cast<drmModePlanePtr>(std::calloc(1, sizeof(drmModePlane)));
  plane->plane_id = id;
  plane->crtc_id = 4;
  return plane;
}
extern "C" int drmSetClientCap(int, uint64_t, uint64_t) { return 0; }
extern "C" int drmModeAtomicAddProperty(drmModeAtomicReq*, uint32_t, uint32_t id, uint64_t value)
{
  staged[id] = value;
  return 0;
}

// Device and GUI boundaries are fakes; DRMAtomic.cpp itself is linked unchanged.
CDRMObject::CDRMObject(int fd) : m_fd(fd) {}
uint32_t CDRMObject::GetPropertyId(std::string_view name) const
{
  if (missingProperty)
    return 0;
  auto [it, inserted] = ids.try_emplace(std::string(name), ids.size() + 1);
  return it->second;
}
bool CDRMObject::CachePropertyValue(uint32_t, uint64_t) { ++cached; return true; }
std::optional<uint64_t> CDRMObject::GetPropertyValue(std::string_view name) const
{
  auto it = values.find(std::string(name));
  return missingProperty || it == values.end() ? std::nullopt : std::optional<uint64_t>(it->second);
}
std::optional<uint64_t> CDRMObject::GetPropertyEnumValue(std::string_view, std::string_view name) const
{
  if (name == "Full") return 1;
  if (name == "Default") return 0;
  if (name == "None") return 2;
  return std::nullopt;
}
std::string CDRMObject::GetTypeName() const { return "fake"; }
std::string CDRMObject::GetPropertyName(uint32_t) const { return "fake"; }
CDRMConnector::CDRMConnector(int fd, uint32_t) : CDRMObject(fd) {}
CDRMCrtc::CDRMCrtc(int fd, uint32_t, int) : CDRMObject(fd)
{
  m_crtc.reset(static_cast<drmModeCrtc*>(std::calloc(1, sizeof(drmModeCrtc))));
  m_crtc->crtc_id = 4;
}
CDRMPlane::CDRMPlane(int fd, uint32_t) : CDRMObject(fd) {}
CDRMUtils::~CDRMUtils() = default;
bool CDRMUtils::OpenDrm(bool) { return true; }
bool CDRMUtils::InitDrm() { return true; }
void CDRMUtils::DestroyDrm() {}
RESOLUTION_INFO CDRMUtils::GetCurrentMode() { std::abort(); }
std::vector<RESOLUTION_INFO> CDRMUtils::GetModes() { return {}; }
bool CDRMUtils::SetMode(const RESOLUTION_INFO&) { return true; }
drm_fb* CDRMUtils::DrmFbGetFromBo(gbm_bo*)
{
  static drm_fb framebuffer{nullptr, 12, DRM_FORMAT_XRGB8888};
  return &framebuffer;
}
uint32_t CDRMUtils::DrmOpaqueFbGetFromBo(gbm_bo*) { return 12; }

class Fixture : public CDRMAtomic
{
  CDRMConnector connector{-1, 1};
  CDRMCrtc crtc{-1, 4, 0};
  CDRMPlane plane{-1, 5};
  drmModeModeInfo mode{};
public:
  Fixture()
  {
    m_connector = &connector;
    m_crtc = &crtc;
    m_gui_plane = &plane;
    m_mode = &mode;
    m_width = mode.hdisplay = 3840;
    m_height = mode.vdisplay = 2160;
    assert(InitDrm());
  }
};

int main()
{
  Fixture drm;
  auto* bo = reinterpret_cast<gbm_bo*>(1);
  rejectTest = true;
  assert(!drm.FlipPageTransactional(bo));
  assert(tests == 1 && commits == 0 && cached == 0);
  rejectTest = false;
  rejectCommit = true;
  assert(!drm.FlipPageTransactional(bo));
  assert(tests == 2 && commits == 1 && cached == 0);
  rejectCommit = false;
  assert(drm.FlipPageTransactional(bo));
  assert(tests == 3 && commits == 2 && cached > 0);
  const int cachedBeforeFailure = cached;
  rejectTest = true;
  assert(!drm.FlipPageTransactional(bo));
  assert(tests == 4 && commits == 2 && cached == cachedBeforeFailure);
  rejectTest = false;
  missingProperty = true;
  assert(!drm.FlipPageTransactional(bo));
  assert(tests == 4 && commits == 2);
  missingProperty = false;
  assert(drm.FlipPageTransactional(bo));
  assert(tests == 5 && commits == 3);
  assert(!drm.FlipPageTransactional(nullptr));
  assert(drm.FlipPageTransactional(bo));
  {
    CDVBridgeState state;
    const size_t before = blobs.size();
    brokenBlob = true;
    assert(!state.Capture(drm) && !state.Captured() && blobs.size() == before);
    brokenBlob = false;
    otherPlane = true;
    assert(!state.Capture(drm) && !state.Captured() && blobs.size() == before);
    otherPlane = false;
    values["DVBRIDGE_DV_STANDARD_LAB"] = 1;
    assert(!state.Capture(drm));
    values["DVBRIDGE_DV_STANDARD_LAB"] = 0;
    assert(state.Capture(drm) && state.Captured());
    assert(blobs.size() == before + 2);
    assert(!state.Capture(drm));
    Fixture differentDevice;
    assert(!state.Stage(differentDevice, false));
    assert(state.Stage(drm, false));
    assert(staged.at(ids.at("DVBRIDGE_DV_STANDARD_LAB")) == 1);
    assert(staged.at(ids.at("HDR_OUTPUT_METADATA")) == 0);
    assert(staged.at(ids.at("max bpc")) == 8);
    assert(staged.at(ids.at("Broadcast RGB")) == 1);
    assert(staged.at(ids.at("Colorspace")) == 0);
    assert(staged.at(ids.at("VRR_ENABLED")) == 0);
    assert(state.Stage(drm, true));
    assert(staged.at(ids.at("DVBRIDGE_DV_STANDARD_LAB")) == 0);
    assert(staged.at(ids.at("max bpc")) == 10);
    assert(staged.at(ids.at("Colorspace")) == 9);
    assert(staged.at(ids.at("VRR_ENABLED")) == 1);
    assert(staged.at(ids.at("alpha")) == 40000);
    const auto restored = staged.at(ids.at("HDR_OUTPUT_METADATA"));
    assert(restored != 42 && blobs.contains(restored));
    state.Restored();
    assert(!state.Captured() && blobs.size() == before);
  }
  std::cout << "PASS: actual DRMAtomic strict path rejects TEST_ONLY/commit/property failures without fallback\n";
}
