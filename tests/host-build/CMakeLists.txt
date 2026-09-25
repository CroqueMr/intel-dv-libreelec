cmake_minimum_required(VERSION 3.22)
project(DVBridgeHostTests LANGUAGES C CXX)
enable_testing()
# Test assertions must remain active even with a Release build configuration.
add_compile_options(-UNDEBUG)
option(DVBRIDGE_TEST_SANITIZERS "Enable address and undefined-behavior sanitizers" ON)
if(DVBRIDGE_TEST_SANITIZERS)
  add_compile_options(-g -O1 -fsanitize=address,undefined -fno-omit-frame-pointer)
  add_link_options(-fsanitize=address,undefined)
endif()
add_subdirectory(../kodi-bridge-build adapters)
get_filename_component(TESTS "${CMAKE_CURRENT_SOURCE_DIR}/.." ABSOLUTE)
foreach(name metadata_transport cm4_bounds presentation_transaction placebo_mapping
             gles_pack gles_reshape render_lifecycle)
  add_executable(${name} "${TESTS}/${name}.c")
  target_link_libraries(${name} PRIVATE dvbridge_core)
  if(name STREQUAL "gles_pack" OR name STREQUAL "render_lifecycle")
    add_test(NAME ${name} COMMAND ${name}
      "${DVBRIDGE_COMMON_SOURCE}/pack_gles300.vert"
      "${DVBRIDGE_COMMON_SOURCE}/pack_gles300.frag")
  else()
    add_test(NAME ${name} COMMAND ${name})
  endif()
endforeach()
target_compile_options(gles_pack PRIVATE -ffp-contract=off)
add_executable(metadata_ownership "${TESTS}/metadata_ownership.cpp")
target_include_directories(metadata_ownership PRIVATE
  "${DVBRIDGE_KODI_SOURCE}/xbmc/cores/VideoPlayer/DVDCodecs/Video")
target_link_libraries(metadata_ownership PRIVATE dvbridge_core)
add_test(NAME metadata_ownership COMMAND metadata_ownership)
set_tests_properties(gles_pack gles_reshape render_lifecycle PROPERTIES ENVIRONMENT
  "LIBGL_ALWAYS_SOFTWARE=1;GALLIUM_DRIVER=llvmpipe;EGL_PLATFORM=surfaceless")

# Optional exact 4K comparison on a real GPU with fragment basic/quad subgroups.
# It is not silently substituted with a software renderer or skipped as a pass.
option(DVBRIDGE_TEST_GPU_EXACT "Build the real-GPU exact transport comparison" OFF)
if(DVBRIDGE_TEST_GPU_EXACT)
  add_executable(fused_exact "${TESTS}/fused_exact.c")
  target_link_libraries(fused_exact PRIVATE dvbridge_core)
  add_test(NAME fused_exact COMMAND fused_exact
    "${DVBRIDGE_COMMON_SOURCE}/pack_gles300.vert"
    "${DVBRIDGE_COMMON_SOURCE}/pack_gles300.frag")
  set_tests_properties(fused_exact PROPERTIES ENVIRONMENT "EGL_PLATFORM=surfaceless")
endif()
