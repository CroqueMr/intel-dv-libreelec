/* SPDX-License-Identifier: GPL-3.0-or-later */
/* Exercise random-access selection with real FFmpeg splitting and deterministic
 * HEVC headers. No test media or hardware is required. */
#include <libavcodec/avcodec.h>
#include "dvbridge_fel_seek.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static int position, seeks;
static bool malformed, missing;
int __wrap_av_seek_frame(AVFormatContext *f,int stream,int64_t pts,int flags)
{
    (void)f; assert(stream==0 && flags==AVSEEK_FLAG_BACKWARD);
    position=pts<0?0:(int)(pts/1000)*24;
    ++seeks;
    return 0;
}
int __wrap_av_read_frame(AVFormatContext *f,AVPacket *p)
{
    (void)f;
    if(position>=240) return AVERROR_EOF;
    uint8_t data[]={0,0,0,1,70,1,64,0,0,0,1,126,1,70,1,64};
    unsigned bp=position%60, ep=(position+53)%60;
    data[6]|=bp|((position%24==0)?128:0);
    data[15]|=ep|((ep==0 && !missing)?128:0);
    assert(av_new_packet(p,sizeof(data))==0);
    memcpy(p->data,data,sizeof(data));
    p->stream_index=0;p->pts=p->dts=position*1000/24;
    ++position;
    return 0;
}
int __wrap_av_parser_parse2(AVCodecParserContext *p,AVCodecContext *c,
    uint8_t **out,int *size_out,const uint8_t *data,int size,
    int64_t pts,int64_t dts,int64_t pos)
{
    (void)c;(void)pts;(void)dts;(void)pos;
    if(malformed) return AVERROR_INVALIDDATA;
    *out=(uint8_t*)data;*size_out=size;
    p->output_picture_number=data[6]&63;p->key_frame=!!(data[6]&128);
    return size;
}
int main(void)
{
    AVFormatContext *f=avformat_alloc_context();assert(f);
    AVStream *s=avformat_new_stream(f,NULL);assert(s);
    s->time_base=(AVRational){1,1000};s->start_time=0;
    s->codecpar->codec_type=AVMEDIA_TYPE_VIDEO;
    s->codecpar->codec_id=AV_CODEC_ID_HEVC;
    /* Target 5s has no EL recovery point; the previous BL key at 2s does. */
    assert(dvbridge_fel_seek_point(f,0,5000)==2000 && seeks<=5);
    missing=true;seeks=0;
    assert(dvbridge_fel_seek_point(f,0,5000)==AV_NOPTS_VALUE && seeks<=5);
    missing=false;malformed=true;seeks=0;
    assert(dvbridge_fel_seek_point(f,0,5000)==AV_NOPTS_VALUE && seeks<=5);
    malformed=false;s->codecpar->video_delay=2;seeks=0;
    assert(dvbridge_fel_seek_point(f,0,5000)==AV_NOPTS_VALUE && seeks<=5);
    avformat_free_context(f);
    puts("PASS: bounded FEL preroll, malformed headers, missing anchors and reordered BL guard");
}
