/* address: 0x00488090 */
/* name: CDXEngine__RenderActiveHudComponentPass */
/* signature: void __fastcall CDXEngine__RenderActiveHudComponentPass(int param_1) */


void __fastcall CDXEngine__RenderActiveHudComponentPass(int param_1)

{
  int iVar1;
  undefined4 *puVar2;
  undefined4 *puVar3;
  float in_stack_ffffffc0;
  float in_stack_ffffffc4;
  float in_stack_ffffffc8;
  float in_stack_ffffffcc;
  float in_stack_ffffffd0;
  float in_stack_ffffffd4;
  float in_stack_ffffffd8;
  float in_stack_ffffffdc;
  float m30;
  float m31;
  float m32;
  float m33;

  if (*(int *)(param_1 + 0x1fc) != 0) {
    CDXEngine__SetRenderState_AlphaSpriteNoDepthWrite();
    DAT_009c68ac = 0;
    DAT_009c690d = 1;
    DAT_009c68ad = 0;
    DAT_009c6910 = 1;
    D3DStateCache__SetState114Raw(0,1,3);
    m30 = 6.658404e-39;
    D3DStateCache__SetState114Raw(0,2,3);
    RenderState_Set(0x17,8);
    m33 = 0.0;
    m32 = 1.96182e-44;
    m31 = 6.658443e-39;
    RenderState_Set(0xe,0);
    puVar2 = &DAT_0067a5e8;
    puVar3 = (undefined4 *)&stack0xffffffc0;
    for (iVar1 = 0xc; iVar1 != 0; iVar1 = iVar1 + -1) {
      *puVar3 = *puVar2;
      puVar2 = puVar2 + 1;
      puVar3 = puVar3 + 1;
    }
    CDXEngine__SetWorldMatrixElements
              (&DAT_009c65c0,DAT_0067a618,DAT_0067a61c,DAT_0067a620,DAT_0067a624,in_stack_ffffffc0,
               in_stack_ffffffc4,in_stack_ffffffc8,in_stack_ffffffcc,in_stack_ffffffd0,
               in_stack_ffffffd4,in_stack_ffffffd8,in_stack_ffffffdc,m30,m31,m32,m33);
    CDXEngine__ApplyPendingRenderState(&DAT_009c65c0,'\0');
    CHudComponent__RenderPass(*(void **)(param_1 + 0x1fc));
    iVar1 = *(int *)(param_1 + 0x1fc);
    if (*(char *)(iVar1 + 100) != '\0') {
      if (iVar1 != 0) {
        (**(code **)(*(int *)(iVar1 + 4) + 4))();
      }
      *(undefined4 *)(param_1 + 0x1fc) = 0;
    }
    DAT_009c68ac = 1;
    DAT_009c690d = 1;
    DAT_009c68ad = 1;
    DAT_009c6910 = 1;
    D3DStateCache__SetState114Raw(0,1,1);
    D3DStateCache__SetState114Raw(0,2,1);
    RenderState_Set(0x17,4);
    RenderState_Set(0xe,1);
  }
  return;
}
