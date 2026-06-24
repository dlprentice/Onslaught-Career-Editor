/* address: 0x00428500 */
/* name: CUnitAI__Unk_00428500 */
/* signature: void __fastcall CUnitAI__Unk_00428500(int param_1) */


void __fastcall CUnitAI__Unk_00428500(int param_1)

{
  int iVar1;
  float unaff_EBX;
  undefined4 *puVar2;
  undefined4 *puVar3;
  undefined1 local_c8 [16];
  float fStack_b8;
  float fStack_b4;
  float fStack_b0;
  float local_a8;
  float local_a4;
  float local_a0;
  float local_98;
  float fStack_94;
  float fStack_90;
  float local_88;
  float fStack_84;
  float fStack_80;
  float local_78;
  float fStack_74;
  float fStack_70;
  void *local_68;
  float local_64;
  float local_60;
  float fStack_5c;
  float fStack_58;
  float local_50;
  float fStack_4c;
  float fStack_48;
  undefined4 auStack_30 [12];

  if (*(int *)(param_1 + 0x278) != DAT_008a9aac) {
    if (((*(byte *)(param_1 + 0x2c) & 4) == 0) || (*(int *)(*(int *)(param_1 + 0x164) + 0x198) == 0)
       ) {
      local_64 = *(float *)(param_1 + 0x254);
      local_68 = *(void **)(param_1 + 0x250);
      CSquadNormal__Helper_004062d0(local_c8,local_68,local_64,0.0,unaff_EBX);
      if (*(int *)(param_1 + 0x26c) != 0) {
        (**(code **)(**(int **)(*(int *)(param_1 + 0x26c) + 0x30) + 0x1c))
                  (s_Component_006248d4,*(undefined4 *)(param_1 + 0x270),param_1 + 0x1c,&local_98,0,
                   0);
      }
      local_50 = local_a8 * local_98 + local_a4 * local_88 + local_a0 * local_78;
      fStack_4c = local_a8 * fStack_94 + local_a4 * fStack_84 + local_a0 * fStack_74;
      fStack_48 = local_a8 * fStack_90 + local_a4 * fStack_80 + local_a0 * fStack_70;
      local_60 = fStack_b8 * local_98 + fStack_b4 * local_88 + fStack_b0 * local_78;
      fStack_5c = fStack_b8 * fStack_94 + fStack_b4 * fStack_84 + fStack_b0 * fStack_74;
      fStack_58 = fStack_b8 * fStack_90 + fStack_b4 * fStack_80 + fStack_b0 * fStack_70;
      Vec3__SetXYZ();
      Mat34__SetRows();
      puVar2 = auStack_30;
      puVar3 = (undefined4 *)(param_1 + 0x3c);
      for (iVar1 = 0xc; iVar1 != 0; iVar1 = iVar1 + -1) {
        *puVar3 = *puVar2;
        puVar2 = puVar2 + 1;
        puVar3 = puVar3 + 1;
      }
    }
    *(int *)(param_1 + 0x278) = DAT_008a9aac;
  }
  return;
}
