/* SPDX-License-Identifier: GPL-3.0-or-later */
#include "DVBridgeGLES.h"
#include "cores/VideoPlayer/DVDCodecs/Video/DVPlaybackInfo.h"
#include <EGL/egl.h>
#include <GLES3/gl3.h>
#include <cassert>
#include <iostream>
#include <vector>
extern "C"
{
#include <libavutil/dovi_meta.h>
#include <libavutil/mem.h>
}

static CDVMetadataBuffer Metadata()
{
  size_t bytes;
  auto* m = av_dovi_metadata_alloc(&bytes);
  assert(m);
  m->num_ext_blocks = 1;
  av_dovi_get_ext(m, 0)->level = 1;
  auto* h = av_dovi_get_header(m);
  h->disable_residual_flag = 1;
  h->bl_bit_depth = h->el_bit_depth = 10;
  h->coef_log2_denom = 12;
  auto* color = av_dovi_get_color(m);
  color->signal_eotf = 65535;
  color->source_max_pq = 3079;
  for (int i = 0; i < 9; ++i)
  {
    color->ycc_to_rgb_matrix[i] = {i % 4 == 0, 1};
    color->rgb_to_lms_matrix[i] = {i % 4 == 0, 1};
  }
  for (int c = 0; c < 3; ++c)
  {
    color->ycc_to_rgb_offset[c] = {0, 1};
    auto& curve = av_dovi_get_mapping(m)->curves[c];
    curve.num_pivots = 2;
    curve.pivots[1] = 1023;
    curve.mapping_idc[0] = AV_DOVI_MAPPING_POLYNOMIAL;
    curve.poly_order[0] = 1;
    curve.poly_coef[0][1] = 4096;
  }
  CDVMetadataBuffer result;
  assert(result.Assign(reinterpret_cast<const uint8_t*>(m), bytes));
  av_free(m);
  return result;
}

int main()
{
  EGLDisplay display = eglGetDisplay(EGL_DEFAULT_DISPLAY);
  assert(eglInitialize(display, nullptr, nullptr) && eglBindAPI(EGL_OPENGL_ES_API));
  const EGLint attributes[] = {EGL_SURFACE_TYPE, EGL_PBUFFER_BIT,
                              EGL_RENDERABLE_TYPE, 0x40, EGL_NONE};
  EGLConfig config;
  EGLint count;
  assert(eglChooseConfig(display, attributes, &config, 1, &count) && count);
  const EGLint sa[] = {EGL_WIDTH, 64, EGL_HEIGHT, 64, EGL_NONE};
  const EGLint ca[] = {EGL_CONTEXT_CLIENT_VERSION, 3, EGL_NONE};
  EGLSurface surface = eglCreatePbufferSurface(display, config, sa);
  EGLContext context = eglCreateContext(display, config, EGL_NO_CONTEXT, ca);
  assert(eglMakeCurrent(display, surface, surface, context));
  {
    CDVBridgeGLES bridge;
    assert(bridge.Initialize(true));
    assert(bridge.Initialize(true));
    assert(bridge.GetPQTexture() == 0);
    assert(!bridge.Pack(0, 3840, 2160, false));
    assert(!bridge.Presented(true));
    assert(CDVPlaybackInfo::presented.load() == 0);
    CDVMetadataBuffer metadata;
    CDVBridgeGLES::Layer layer{};
    assert(!bridge.Prepare(layer, nullptr, metadata, {}));
    bridge.Reset();
    assert(!bridge.Presented(false));

    GLuint textures[3], framebuffer;
    glGenTextures(3, textures);
    const std::vector<uint16_t> pixels(64 * 64, 512 << 6);
    for (int i = 0; i < 2; ++i)
    {
      glBindTexture(GL_TEXTURE_2D, textures[i]);
      glTexImage2D(GL_TEXTURE_2D, 0, i ? 0x822C : 0x822A, i ? 32 : 64,
                   i ? 32 : 64, 0, i ? GL_RG : GL_RED, GL_UNSIGNED_SHORT, pixels.data());
      glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
      glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
    }
    glBindTexture(GL_TEXTURE_2D, textures[2]);
    glTexStorage2D(GL_TEXTURE_2D, 1, GL_RGBA8, 3840, 2160);
    glGenFramebuffers(1, &framebuffer);
    glBindFramebuffer(GL_FRAMEBUFFER, framebuffer);
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, textures[2], 0);
    assert(glCheckFramebufferStatus(GL_FRAMEBUFFER) == GL_FRAMEBUFFER_COMPLETE);
    assert(glGetError() == GL_NO_ERROR);
    layer = {DVBRIDGE_P010, 64, 64, {{textures[0], 64, 64}, {textures[1], 32, 32}}, 0.0};
    metadata = Metadata();
    const dvbridge_geometry geometry{64, 64, 840, 0, 2160, 2160};
    assert(bridge.Prepare(layer, nullptr, metadata, geometry));
    assert(bridge.GetPQTexture());
    glBindFramebuffer(GL_DRAW_FRAMEBUFFER, framebuffer);
    assert(bridge.GetPQFramebuffer());
    GLint currentFramebuffer;
    glGetIntegerv(GL_DRAW_FRAMEBUFFER_BINDING, &currentFramebuffer);
    assert(static_cast<GLuint>(currentFramebuffer) == framebuffer);
    assert(!bridge.Presented(true)); // An unpacked frame must never advance metadata.
    assert(!bridge.GetPQTexture());
    assert(bridge.Prepare(layer, nullptr, metadata, geometry));
    assert(bridge.Pack(framebuffer, 3840, 2160, false));
    assert(!bridge.Presented(false)); // Failed scanout invalidates the candidate.
    assert(!bridge.GetPQTexture());
    assert(bridge.Prepare(layer, nullptr, metadata, geometry));
    assert(bridge.Pack(framebuffer, 3840, 2160, false));
    assert(bridge.Presented(true));
    assert(CDVPlaybackInfo::presented.load() == CDVPlaybackInfo::HDMI);
    assert(!bridge.Presented(true));
    assert(CDVPlaybackInfo::presented.load() == 0);
    assert(bridge.Prepare(layer, nullptr, metadata, geometry));
    assert(!bridge.Pack(framebuffer, 1920, 1080, false));
    assert(!bridge.Presented(true));
    assert(CDVPlaybackInfo::presented.load() == 0);
    assert(bridge.Prepare(layer, nullptr, metadata, geometry));
    assert(bridge.Pack(framebuffer, 3840, 2160, false));
    assert(bridge.Presented(true));
    bridge.Reset();
    assert(CDVPlaybackInfo::presented.load() == 0);
    assert(glIsTexture(textures[0]) && glIsTexture(textures[1]));
    glDeleteFramebuffers(1, &framebuffer);
    glDeleteTextures(3, textures);
  }
  eglMakeCurrent(display, EGL_NO_SURFACE, EGL_NO_SURFACE, EGL_NO_CONTEXT);
  eglDestroyContext(display, context);
  eglDestroySurface(display, surface);
  eglTerminate(display);
  std::cout << "PASS: Kodi C++ P010/render/pack lifecycle, failed presentation, duplicate commit and size gates\n";
}
