/* address: 0x0053b470 */
/* name: CDXBattleLine__RenderTriOverlayPass */
/* signature: void __fastcall CDXBattleLine__RenderTriOverlayPass(int param_1) */


void __fastcall CDXBattleLine__RenderTriOverlayPass(int param_1)

{
  void *value;

  if ((*(int *)(param_1 + 0x5c) != 0) && (*(int *)(param_1 + 0x78) != 0)) {
    CVBuffer__Unlock();
    *(undefined4 *)(param_1 + 0x5c) = 0;
  }
  if (*(int *)(param_1 + 0x60) != 0) {
    value = CDXTexture__GetAnimatedFrame(*(void **)(param_1 + 0xc));
    CEngine__SetRenderStateCached(&DAT_00855bb0,0,(int)value);
    CVBuffer__SetStreamSource(0);
    RenderState_Set(0x9c,1);
    RenderState_Set(0x9d,0);
    RenderState_Set(0x13,5);
    RenderState_Set(0x14,6);
    D3DStateCache__SetStateCached(0,2,2);
    D3DStateCache__SetStateCached(0,3,3);
    RenderState_Set(0x3c,0);
    D3DStateCache__SetStateCached(0,1,4);
    D3DStateCache__SetStateCached(0,2,2);
    D3DStateCache__SetStateCached(0,4,2);
    D3DStateCache__SetStateCached(0,5,2);
    CDXEngine__ApplyPendingRenderState(&DAT_009c65c0,'\0');
    (**(code **)(*DAT_00888a50 + 0x144))(DAT_00888a50,1,0,*(undefined4 *)(param_1 + 0x60));
    RenderState_Set(0x13,2);
    RenderState_Set(0x14,2);
    D3DStateCache__SetStateCached(0,3,0);
    CDXEngine__ApplyPendingRenderState(&DAT_009c65c0,'\0');
    (**(code **)(*DAT_00888a50 + 0x144))(DAT_00888a50,1,0,*(undefined4 *)(param_1 + 0x60));
    RenderState_Set(0x9c,0);
  }
  return;
}
