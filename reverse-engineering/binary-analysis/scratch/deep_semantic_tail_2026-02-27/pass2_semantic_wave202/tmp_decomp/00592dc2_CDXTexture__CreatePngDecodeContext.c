/* address: 0x00592dc2 */
/* name: CDXTexture__CreatePngDecodeContext */
/* signature: void * __stdcall CDXTexture__CreatePngDecodeContext(void * param_1, int param_2, int param_3, int param_4) */


void * CDXTexture__CreatePngDecodeContext(void *param_1,int param_2,int param_3,int param_4)

{
  void *pvVar1;
  int iVar2;
  void *pvVar3;
  int extraout_EAX;
  char *pcVar4;

  pvVar1 = (void *)CDXTexture__AllocZeroedDecodeState(1);
  if (pvVar1 == (void *)0x0) {
    return (void *)0x0;
  }
  iVar2 = __setjmp3(pvVar1,0);
  if (iVar2 != 0) {
    CDXTexture__FreeDecodeStateIfOwnerPresent((int)pvVar1,*(int *)((int)pvVar1 + 0x9c));
    CDXTexture__FreeDecodeState((int)pvVar1);
    return (void *)0x0;
  }
  CTexture__SetDecodeContextTriplet((int)pvVar1,param_2,param_3,param_4);
  if ((param_1 == (void *)0x0) || (*(char *)param_1 != '1')) {
    CDXTexture__ThrowDecodeError(pvVar1,0x5ee950);
  }
  *(undefined4 *)((int)pvVar1 + 0xa0) = 0x2000;
  pvVar3 = CMeshCollisionVolume__Helper_0059cc7c(pvVar1,0x2000);
  *(void **)((int)pvVar1 + 0x9c) = pvVar3;
  *(code **)((int)pvVar1 + 0x84) = CDXTexture__AllocZeroedDecodeBuffer;
  *(code **)((int)pvVar1 + 0x88) = CDXTexture__FreeDecodeBufferIfPresent;
  *(void **)((int)pvVar1 + 0x8c) = pvVar1;
  CDXTexture__InflateInit_WindowBits15((int)pvVar1 + 100,"1.1.4",0x38);
  if (extraout_EAX == -6) {
    pcVar4 = "zlib version error";
  }
  else if ((extraout_EAX == -4) || (extraout_EAX == -2)) {
    pcVar4 = "zlib memory error";
  }
  else {
    if (extraout_EAX == 0) goto LAB_00592e93;
    pcVar4 = "Unknown zlib error";
  }
  CDXTexture__ThrowDecodeError(pvVar1,(int)pcVar4);
LAB_00592e93:
  *(undefined4 *)((int)pvVar1 + 0x70) = *(undefined4 *)((int)pvVar1 + 0x9c);
  *(undefined4 *)((int)pvVar1 + 0x74) = *(undefined4 *)((int)pvVar1 + 0xa0);
  CDXTexture__SetReadFunction((int)pvVar1,0,0);
  return pvVar1;
}
