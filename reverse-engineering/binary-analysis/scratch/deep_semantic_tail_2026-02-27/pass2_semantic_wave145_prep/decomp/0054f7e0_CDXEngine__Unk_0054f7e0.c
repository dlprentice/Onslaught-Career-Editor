/* address: 0x0054f7e0 */
/* name: CDXEngine__Unk_0054f7e0 */
/* signature: void __fastcall CDXEngine__Unk_0054f7e0(int param_1) */


void __fastcall CDXEngine__Unk_0054f7e0(int param_1)

{
  undefined4 *puVar1;
  int *piVar2;
  undefined4 *extraout_EAX;
  int iVar3;
  undefined4 unaff_EBX;
  undefined4 *puVar4;
  undefined1 *puVar5;
  undefined4 local_54;
  undefined4 uStack_50;
  undefined4 uStack_4c;
  undefined1 auStack_44 [16];
  undefined1 auStack_34 [4];
  undefined1 local_30 [48];

  DAT_009c68ad = 0;
  DAT_009c6910 = 1;
  RenderState_Set(0x16,1);
  RenderState_Set(0xf,0);
  D3DStateCache__SetStateCached(0,1,4);
  RenderState_Set(0x13,2);
  RenderState_Set(0x14,6);
  D3DStateCache__SetStateCached(0,5,2);
  D3DStateCache__SetStateCached(0,6,0);
  D3DStateCache__SetStateCached(0,4,4);
  RenderState_Set(0xe,0);
  DAT_009c68ac = 0;
  DAT_009c690d = 1;
  RenderState_Set(0xf,0);
  puVar1 = (undefined4 *)(param_1 + 0x20);
  *puVar1 = 0x3f800000;
  puVar4 = (undefined4 *)(param_1 + 0x30);
  *(undefined4 *)(param_1 + 0x24) = 0;
  *(undefined4 *)(param_1 + 0x28) = 0;
  *(undefined4 *)(param_1 + 0x2c) = local_54;
  *puVar4 = 0;
  *(undefined4 *)(param_1 + 0x34) = 0x3f800000;
  *(undefined4 *)(param_1 + 0x38) = 0;
  *(undefined4 *)(param_1 + 0x3c) = local_54;
  puVar5 = local_30;
  (**(code **)(*(int *)(&DAT_0089c9a4)[DAT_0089ce4c] + 4))();
  local_54 = 0;
  uStack_50 = 0x3f800000;
  uStack_4c = 0;
  CSquadNormal__Helper_0040d2c0(auStack_34,auStack_44,&local_54,puVar5);
  local_54 = 0;
  uStack_50 = 0;
  uStack_4c = 0xbf800000;
  CSquadNormal__Helper_0040d2c0(auStack_34,&stack0xffffff9c,&local_54,puVar5);
  Vec3__Cross(auStack_44,&local_54,&stack0xffffff9c,puVar5);
  *puVar1 = *extraout_EAX;
  *(undefined4 *)(param_1 + 0x24) = extraout_EAX[1];
  *(undefined4 *)(param_1 + 0x28) = extraout_EAX[2];
  *(undefined4 *)(param_1 + 0x2c) = extraout_EAX[3];
  SQRT__Wrapper_00406d50(puVar1);
  *puVar4 = unaff_EBX;
  *(undefined4 *)(param_1 + 0x34) = 0;
  *(undefined4 *)(param_1 + 0x38) = 0x3f800000;
  *(undefined4 *)(param_1 + 0x3c) = 0;
  SQRT__Wrapper_00406d50(puVar4);
  for (piVar2 = DAT_0082b404; piVar2 != (int *)0x0; piVar2 = (int *)piVar2[0x10]) {
    iVar3 = (**(code **)(*piVar2 + 4))();
    if (iVar3 != 0xb) {
      (**(code **)(*piVar2 + 0x5c))(1);
    }
  }
  DXParticleTexture__RenderAll();
  RenderState_Set(0xe,1);
  DAT_009c68ad = 1;
  DAT_009c6910 = 1;
  RenderState_Set(0x13,5);
  RenderState_Set(0x14,6);
  RenderState_Set(0x1b,1);
  RenderState_Set(0xf,1);
  DAT_009c68ac = 1;
  DAT_009c690d = 1;
  RenderState_Set(0x16,3);
  D3DStateCache__SetStateCached(0,1,4);
  return;
}
