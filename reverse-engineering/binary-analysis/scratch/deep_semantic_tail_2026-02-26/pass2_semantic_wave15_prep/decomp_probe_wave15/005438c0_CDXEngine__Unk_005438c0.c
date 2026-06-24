/* address: 0x005438c0 */
/* name: CDXEngine__Unk_005438c0 */
/* signature: void CDXEngine__Unk_005438c0(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CDXEngine__Unk_005438c0(void)

{
  void *value;
  int iVar1;
  undefined4 *puVar2;
  undefined4 *puVar3;
  void *in_stack_ffffff74;
  float in_stack_ffffff78;
  float in_stack_ffffff7c;
  float in_stack_ffffff80;
  float in_stack_ffffff84;
  float in_stack_ffffff88;
  float in_stack_ffffff8c;
  float in_stack_ffffff90;
  float m30;
  float m31;
  float m32;
  float m33;
  float local_34;
  undefined4 local_30 [4];
  undefined4 local_20;
  undefined4 local_1c;
  undefined4 local_18;
  undefined4 local_10;
  undefined4 local_c;
  undefined4 local_8;

  if ((DAT_0067a67c != 0) && (DAT_0067a678 != 0)) {
    if (DAT_008aa8d0 != '\0') {
      DAT_009c68ac = 0;
      DAT_009c690d = 1;
      RenderState_Set(0x1b,0);
      RenderState_Set(0xf,1);
      CDXEngine__ApplyPendingRenderState(&DAT_009c65c0,'\0');
      in_stack_ffffff90 = 1.0;
      in_stack_ffffff8c = 1.0;
      in_stack_ffffff88 = -NAN;
      in_stack_ffffff84 = 0.0;
      in_stack_ffffff80 = 1.0;
      in_stack_ffffff7c = 0.0;
      in_stack_ffffff78 = 5.60519e-45;
      in_stack_ffffff74 = DAT_008aa8b8;
      CVBufTexture__DrawSpriteEx
                (400.0,300.0,0.0,DAT_008aa8b8,4,0,1.0,0.0,-NAN,1.0,1.0,0.0,1.0,0.0,1.0);
    }
    D3DStateCache__SetState114Raw(0,5,1);
    m33 = 1.4013e-45;
    m32 = 8.40779e-45;
    m31 = 0.0;
    m30 = 7.73481e-39;
    D3DStateCache__SetState114Raw(0,6,1);
    local_30[0] = 0x3f800000;
    local_30[1] = 0;
    local_30[2] = 0;
    local_20 = 0;
    local_1c = 0x3f800000;
    local_18 = 0;
    local_10 = 0;
    local_c = 0;
    local_8 = 0x3f800000;
    puVar2 = local_30;
    puVar3 = (undefined4 *)&stack0xffffff74;
    for (iVar1 = 0xc; iVar1 != 0; iVar1 = iVar1 + -1) {
      *puVar3 = *puVar2;
      puVar2 = puVar2 + 1;
      puVar3 = puVar3 + 1;
    }
    CDXEngine__SetWorldMatrixElements
              (&DAT_009c65c0,0.0,0.0,0.0,local_34,(float)in_stack_ffffff74,in_stack_ffffff78,
               in_stack_ffffff7c,in_stack_ffffff80,in_stack_ffffff84,in_stack_ffffff88,
               in_stack_ffffff8c,in_stack_ffffff90,m30,m31,m32,m33);
    (**(code **)(*DAT_00888a50 + 0xc4))();
    DAT_009c68ad = 1;
    DAT_009c6910 = 1;
    RenderState_Set(0x13,5);
    RenderState_Set(0x14,6);
    RenderState_Set(0x1b,0);
    RenderState_Set(0xf,1);
    RenderState_Set(0x18,8);
    D3DStateCache__SetStateCached(0,2,2);
    D3DStateCache__SetStateCached(0,3,0);
    D3DStateCache__SetSlotMode4or5(0);
    D3DStateCache__SetStateCached(0,5,2);
    D3DStateCache__SetStateCached(0,4,2);
    value = CDXTexture__GetAnimatedFrame(DAT_008aa8b8);
    CEngine__SetRenderStateCached(&DAT_00855bb0,0,(int)value);
    if (DAT_008aa8b4 != 0) {
      CVBufTexture__RenderIndexed();
    }
    DAT_009c68ad = 0;
    DAT_009c6910 = 1;
    RenderState_Set(0x3c,-1);
    D3DStateCache__SetStateCached(0,2,2);
    D3DStateCache__SetStateCached(0,3,3);
    D3DStateCache__SetSlotMode4or5(0);
    RenderState_Set(0x18,8);
    CVBufTexture__RenderIndexed();
    RenderState_Set(0x13,5);
    RenderState_Set(0x14,6);
    D3DStateCache__SetStateCached(0,2,2);
    D3DStateCache__SetStateCached(0,3,0);
    D3DStateCache__SetStateCached(0,1,4);
    D3DStateCache__SetState114Raw(1,5,1);
    D3DStateCache__SetState114Raw(1,6,1);
    D3DStateCache__SetStateCached(1,0xb,1);
    D3DStateCache__SetStateCached(1,0x1a,3);
    D3DStateCache__SetStateCached(1,2,2);
    D3DStateCache__SetStateCached(1,3,1);
    D3DStateCache__SetStateCached(1,1,1);
    D3DStateCache__SetStateCached(1,4,1);
    D3DStateCache__SetStateCached(1,6,1);
    D3DStateCache__SetState114Raw(2,5,1);
    D3DStateCache__SetState114Raw(2,6,1);
    D3DStateCache__SetStateCached(2,1,1);
    D3DStateCache__SetStateCached(2,5,2);
    D3DStateCache__SetStateCached(2,4,1);
    CEngine__SetRenderStateCached(&DAT_00855bb0,2,0);
    D3DStateCache__SetStateCached(2,0xb,2);
    RenderState_SetAlphaRefCached(8);
    D3DStateCache__SetState114Raw(0,5,2);
    D3DStateCache__SetState114Raw(0,6,2);
    D3DStateCache__SetState114Raw(1,5,2);
    D3DStateCache__SetState114Raw(1,6,2);
    D3DStateCache__SetState114Raw(2,5,2);
    D3DStateCache__SetState114Raw(2,6,2);
    RenderState_Set(0x1b,1);
    DAT_009c68ad = 1;
    DAT_009c6910 = 1;
  }
  return;
}
