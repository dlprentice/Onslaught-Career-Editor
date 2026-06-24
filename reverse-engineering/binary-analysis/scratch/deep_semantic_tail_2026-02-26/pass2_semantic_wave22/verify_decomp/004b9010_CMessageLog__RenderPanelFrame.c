/* address: 0x004b9010 */
/* name: CMessageLog__RenderPanelFrame */
/* signature: int CMessageLog__RenderPanelFrame(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CMessageLog__RenderPanelFrame(void)

{
  int iVar1;
  float p2;
  float p1;
  float p1_00;
  float p2_00;
  int iVar2;
  int extraout_EAX;
  int in_ECX;
  float p9;
  int in_stack_00000004;
  int in_stack_00000008;
  int in_stack_0000000c;
  int in_stack_00000010;
  float in_stack_00000014;
  int local_8;

  local_8 = (int)(longlong)ROUND(in_stack_00000014 * _DAT_005dc568);
  if (in_stack_0000000c < 0x40) {
    in_stack_0000000c = 0x40;
  }
  if (in_stack_00000010 < 0x40) {
    in_stack_00000010 = 0x40;
  }
  RenderState_Set(0x17,8);
  CDXEngine__ApplyPendingRenderState(&DAT_009c65c0,'\0');
  p2 = (float)in_stack_00000008;
  p1 = (float)in_stack_00000004;
  p9 = (float)(local_8 << 0x18);
  CVBufTexture__DrawSpriteEx
            (p1,p2,0.004,*(void **)(in_ECX + 8),0,0,1.0,0.0,p9,1.0,1.0,1.0,0.0,0.0,1.0);
  p1_00 = ((float)in_stack_0000000c + p1) - _DAT_005db2b8;
  CVBufTexture__DrawSpriteEx
            (p1_00,p2,0.004,*(void **)(in_ECX + 8),0,0,1.0,0.0,p9,1.0,1.0,0.0,1.0,0.0,1.0);
  p2_00 = ((float)in_stack_00000010 + p2) - _DAT_005db2b8;
  CVBufTexture__DrawSpriteEx
            (p1_00,p2_00,0.004,*(void **)(in_ECX + 8),0,0,1.0,3.1415927,p9,1.0,1.0,1.0,0.0,0.0,1.0);
  CVBufTexture__DrawSpriteEx
            (p1,p2_00,0.004,*(void **)(in_ECX + 8),0,0,1.0,3.1415927,p9,1.0,1.0,0.0,1.0,0.0,1.0);
  iVar1 = in_stack_0000000c + -0x40;
  if (iVar1 != 0) {
    CVBufTexture__DrawSpriteEx
              ((float)(in_stack_00000004 + 0x20),p2,0.004,*(void **)(in_ECX + 0xc),0,0,1.0,0.0,p9,
               (float)iVar1 * _DAT_005dbb50,2.0,0.0,1.0,0.0,1.0);
    CVBufTexture__DrawSpriteEx
              ((float)(in_stack_00000004 + 0x20),
               (float)(in_stack_00000008 + -0x20 + in_stack_00000010),0.004,*(void **)(in_ECX + 0xc)
               ,0,0,1.0,0.0,p9,(float)iVar1 * _DAT_005dbb50,2.0,0.0,1.0,0.0,1.0);
  }
  iVar2 = in_stack_00000010 + -0x40;
  if (iVar2 != 0) {
    CVBufTexture__DrawSpriteEx
              (p1,(float)(in_stack_00000008 + 0x20),0.004,*(void **)(in_ECX + 0xc),0,0,1.0,0.0,p9,
               2.0,(float)iVar2 * _DAT_005dbb50,0.0,1.0,0.0,1.0);
    CVBufTexture__DrawSpriteEx
              ((float)(in_stack_00000004 + -0x20 + in_stack_0000000c),
               (float)(in_stack_00000008 + 0x20),0.004,*(void **)(in_ECX + 0xc),0,0,1.0,0.0,p9,2.0,
               (float)iVar2 * _DAT_005dbb50,0.0,1.0,0.0,1.0);
  }
  if ((iVar1 != 0) && (iVar2 != 0)) {
    CVBufTexture__DrawSpriteEx
              ((float)(in_stack_00000004 + 0x20),(float)(in_stack_00000008 + 0x20),0.004,
               *(void **)(in_ECX + 0xc),0,0,1.0,0.0,p9,(float)iVar1 * _DAT_005dbb50,
               (float)iVar2 * _DAT_005dbb50,0.0,1.0,0.0,1.0);
  }
  RenderState_Set(0x17,4);
  CDXEngine__ApplyPendingRenderState(&DAT_009c65c0,'\0');
  return extraout_EAX;
}
