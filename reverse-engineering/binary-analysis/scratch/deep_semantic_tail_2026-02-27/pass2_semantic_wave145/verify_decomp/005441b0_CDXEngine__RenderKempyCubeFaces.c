/* address: 0x005441b0 */
/* name: CDXEngine__RenderKempyCubeFaces */
/* signature: void __fastcall CDXEngine__RenderKempyCubeFaces(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CDXEngine__RenderKempyCubeFaces(int param_1)

{
  undefined4 *puVar1;
  float *pfVar2;
  void *value;
  int iVar3;
  undefined4 *puVar4;
  undefined4 *puVar5;
  undefined1 *m10;
  float in_stack_ffffffb0;
  float in_stack_ffffffb4;
  float in_stack_ffffffb8;
  float in_stack_ffffffbc;
  float in_stack_ffffffc0;
  float in_stack_ffffffc4;
  float in_stack_ffffffc8;
  float in_stack_ffffffcc;
  float m31;
  float m32;
  float m33;
  undefined1 local_10 [16];

  RenderState_Set(0xe,0);
  RenderState_Set(7,0);
  D3DStateCache__SetState114Raw(0,1,3);
  D3DStateCache__SetState114Raw(0,2,3);
  m33 = 1.4013e-45;
  m32 = 0.0;
  DAT_009c68ac = 0;
  DAT_009c690d = 1;
  DAT_009c68ad = 0;
  DAT_009c6910 = 1;
  m31 = 7.737906e-39;
  D3DStateCache__SetStateCached(0,1,4);
  puVar1 = (undefined4 *)(&DAT_0089c9a4)[DAT_0089ce4c];
  puVar4 = &DAT_008aa8d8;
  puVar5 = (undefined4 *)&stack0xffffffb0;
  for (iVar3 = 0xc; iVar3 != 0; iVar3 = iVar3 + -1) {
    *puVar5 = *puVar4;
    puVar4 = puVar4 + 1;
    puVar5 = puVar5 + 1;
  }
  m10 = local_10;
  pfVar2 = (float *)(**(code **)*puVar1)();
  CDXEngine__SetWorldMatrixElements
            (&DAT_009c65c0,*pfVar2,pfVar2[1],pfVar2[2],pfVar2[3],(float)m10,in_stack_ffffffb0,
             in_stack_ffffffb4,in_stack_ffffffb8,in_stack_ffffffbc,in_stack_ffffffc0,
             in_stack_ffffffc4,in_stack_ffffffc8,in_stack_ffffffcc,m31,m32,m33);
  (**(code **)(*DAT_00888a50 + 400))();
  _DAT_009c73d4 = 0x102;
  DAT_009c741c = 1;
  CDXEngine__ApplyPendingRenderState(&DAT_009c65c0,'\0');
  RenderState_SetRaw(0x98,0);
  iVar3 = 0;
  do {
    value = CDXTexture__GetAnimatedFrame(*(void **)(iVar3 + param_1));
    CEngine__SetRenderStateCached(&DAT_00855bb0,0,(int)value);
    (**(code **)(*DAT_00888a50 + 0x144))();
    iVar3 = iVar3 + 4;
  } while (iVar3 < 0x14);
  CEngine__Helper_004eba30(0);
  RenderState_Set(0xe,1);
  RenderState_Set(7,1);
  D3DStateCache__SetState114Raw(0,1,1);
  D3DStateCache__SetState114Raw(0,2,1);
  DAT_009c68ad = 1;
  DAT_009c6910 = 1;
  DAT_009c68ac = 1;
  DAT_009c690d = 1;
  return;
}
