/* SPDX-License-Identifier: GPL-3.0-or-later */
#include "dvbridge_fel.h"
#include <libavutil/hwcontext.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>

/* Real splitter and ownership, deterministic parser/decoder without VAAPI. */
static int64_t ready[64];
static unsigned count;
static bool end, bad_pts, send_error, parse_error;
int __wrap_av_parser_parse2(AVCodecParserContext *p, AVCodecContext *c,
    uint8_t **out, int *size_out, const uint8_t *data, int size,
    int64_t pts, int64_t dts, int64_t pos)
{
    (void)c; (void)pts; (void)dts; (void)pos;
    if (parse_error) return AVERROR_INVALIDDATA;
    assert(size>=7); *out=(uint8_t *)data; *size_out=size;
    p->output_picture_number=data[6]&63; p->key_frame=!!(data[6]&128);
    return size;
}
int __wrap_avcodec_open2(AVCodecContext *c,const AVCodec *codec,AVDictionary **o)
{ (void)codec; (void)o; assert(c->hw_device_ctx && c->get_format && c->thread_count==1); return 0; }
void __wrap_avcodec_flush_buffers(AVCodecContext *c)
{ (void)c; count=0; end=false; }
int __wrap_avcodec_send_packet(AVCodecContext *c,const AVPacket *p)
{
    (void)c;
    if (send_error) return AVERROR_INVALIDDATA;
    if (!p) { end=true; return 0; }
    assert(p->size==7 && p->data[4]==70 && p->data[5]==1 && count<64);
    ready[count++]=p->pts; return 0;
}
int __wrap_avcodec_receive_frame(AVCodecContext *c,AVFrame *frame)
{
    (void)c;
    if (!count) return end ? AVERROR_EOF : AVERROR(EAGAIN);
    frame->format=AV_PIX_FMT_VAAPI; frame->pts=bad_pts ? AV_NOPTS_VALUE : ready[0];
    frame->best_effort_timestamp=AV_NOPTS_VALUE;
    frame->buf[0]=av_buffer_alloc(8); assert(frame->buf[0]);
    --count; memmove(ready,ready+1,count*sizeof(*ready)); return 0;
}
static bool submit(struct dvbridge_fel *f,int64_t pts,unsigned b,unsigned e,bool bk,bool ek)
{
    uint8_t bytes[]={0,0,0,1,70,1,64,0,0,0,1,126,1,70,1,64};
    assert(b<64 && e<64); bytes[6]|=b|(bk?128:0); bytes[15]|=e|(ek?128:0);
    AVPacket *p=av_packet_alloc(); assert(p && av_new_packet(p,sizeof(bytes))==0);
    memcpy(p->data,bytes,sizeof(bytes)); p->pts=p->dts=pts;
    bool result=dvbridge_fel_submit(f,p);
    assert(p->size==16 && p->data[11]==126 && p->pts==pts);
    av_packet_free(&p); return result;
}
static void take(struct dvbridge_fel *f,int64_t pts)
{ AVFrame *frame=NULL; assert(dvbridge_fel_take(f,pts,&frame)==1 && frame->pts==pts); av_frame_free(&frame); }
int main(void)
{
    AVCodecParameters *p=avcodec_parameters_alloc(); assert(p);
    p->codec_type=AVMEDIA_TYPE_VIDEO; p->codec_id=AV_CODEC_ID_HEVC; p->width=3840; p->height=2160;
    struct dvbridge_fel *f=dvbridge_fel_create(p,(AVRational){1,1000000}); assert(f);
    avcodec_parameters_free(&p);
    AVBufferRef *device=av_buffer_allocz(sizeof(AVHWDeviceContext)); assert(device);
    ((AVHWDeviceContext *)device->data)->type=AV_HWDEVICE_TYPE_VAAPI;
    AVFrame *frame=NULL;
    assert(submit(f,0,0,0,true,true)); assert(dvbridge_fel_take(f,0,&frame)==0);
    assert(dvbridge_fel_device(f,device)); take(f,0);
    assert(submit(f,42000,1,3,false,false)); assert(submit(f,83000,2,1,false,false));
    assert(dvbridge_fel_take(f,42000,&frame)==0);
    assert(submit(f,125000,3,2,false,false)); take(f,42000); take(f,83000); take(f,125000);
    assert(submit(f,167000,4,0,false,true)); take(f,167000); /* Independent EL IDR. */
    assert(submit(f,209000,5,2,false,false)); assert(submit(f,250000,6,1,false,false));
    take(f,209000); take(f,250000);
    assert(dvbridge_fel_drain(f)); assert(dvbridge_fel_take(f,999999,&frame)==-1);
    assert(!submit(f,999999,7,3,false,false));
    dvbridge_fel_reset(f); assert(submit(f,0,0,0,true,true));
    assert(dvbridge_fel_take(f,0,&frame)==1); assert(dvbridge_fel_take(f,0,&frame)==-1);
    dvbridge_fel_reset(f); assert(frame->buf[0]); av_frame_free(&frame);
    assert(submit(f,0,0,0,true,true)); assert(!submit(f,0,0,0,false,false));
    dvbridge_fel_reset(f); bad_pts=true; assert(!submit(f,0,0,0,true,true)); bad_pts=false;
    dvbridge_fel_reset(f); parse_error=true; assert(!submit(f,0,0,0,true,true)); parse_error=false;
    dvbridge_fel_reset(f); send_error=true; assert(!submit(f,0,0,0,true,true)); send_error=false;
    dvbridge_fel_reset(f);
    assert(submit(f,0,0,0,true,true)); take(f,0);
    for (unsigned i=1;i<=32;i++) assert(submit(f,i*41708,i,63,false,false));
    assert(!submit(f,33*41708,33,63,false,false));
    /* A BL recovery point need not be an EL random-access point. */
    dvbridge_fel_reset(f); assert(submit(f,1000000,20,7,true,false));
    assert(dvbridge_fel_take(f,1000000,&frame)==2 && !frame);
    assert(submit(f,1042000,21,0,false,true)); take(f,1042000);
    assert(dvbridge_fel_take(f,1000000,&frame)==2 && !frame);
    assert(submit(f,1083000,22,1,false,false)); take(f,1083000);
    /* Both layers can instead share a non-zero CRA picture identity. */
    dvbridge_fel_reset(f); assert(submit(f,2000000,42,42,true,true)); take(f,2000000);
    assert(submit(f,2042000,43,43,false,false)); take(f,2042000);
    /* Neither EOF nor unlimited preroll may hide a missing recovery point. */
    dvbridge_fel_reset(f);
    assert(submit(f,0,20,7,true,false));
    assert(!dvbridge_fel_drain(f) && dvbridge_fel_failed(f));
    assert(dvbridge_fel_take(f,0,&frame)==-1 && !frame);
    dvbridge_fel_reset(f);
    for (unsigned i=0;i<1024;i++)
        assert(submit(f,i*41708,20,7,false,false));
    assert(!submit(f,1024*41708,20,7,false,false));
    assert(dvbridge_fel_failed(f));
    dvbridge_fel_destroy(f); av_buffer_unref(&device);
    puts("PASS: HEVC picture mapping, independent IDR, ownership, reset, bounded lookahead and errors");
}
