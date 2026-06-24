/* address: 0x0049fdb0 */
/* name: CComponent__Unk_0049fdb0 */
/* signature: void __fastcall CComponent__Unk_0049fdb0(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CComponent__Unk_0049fdb0(int param_1)

{
  int iVar1;
  float fVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  int iVar7;
  int iVar8;
  float *pfVar9;
  void *unaff_EDI;
  float *pfVar10;
  undefined1 auStack_8c [4];
  void *pvStack_88;
  float fStack_84;
  float fStack_80;
  float fStack_7c;
  float fStack_78;
  int local_74;
  int local_70;
  float fStack_6c;
  float fStack_68;
  float fStack_64;
  undefined4 uStack_60;
  float fStack_5c;
  float fStack_58;
  float fStack_54;
  float fStack_4c;
  float fStack_48;
  float fStack_44;
  float afStack_3c [4];
  float fStack_2c;
  float fStack_28;
  float fStack_24;
  float fStack_1c;
  float fStack_18;
  float fStack_14;
  void *local_c;
  undefined1 *puStack_8;
  undefined4 uStack_4;

  uStack_4 = 0xffffffff;
  puStack_8 = &LAB_005d344b;
  local_c = ExceptionList;
  if (*(int *)(*(int *)(param_1 + 0x164) + 0x130) != 0) {
    ExceptionList = &local_c;
    local_70 = param_1;
    local_74 = CWorldPhysicsManager__Helper_004cd7a0
                         (&DAT_0082b400,s_Generic_Mesh_00623b94,unaff_EDI);
    if (((*(int **)(param_1 + 0x30) != (int *)0x0) &&
        (iVar3 = (**(code **)(**(int **)(param_1 + 0x30) + 0x24))(), iVar3 != 0)) &&
       (iVar8 = 0, 0 < *(int *)(iVar3 + 0x15c))) {
      do {
        if (*(int *)(*(int *)(*(int *)(iVar3 + 0x160) + iVar8 * 4) + 0x8c) == 1) {
          pvStack_88 = (void *)0x0;
          CWorldPhysicsManager__Helper_004cb040(auStack_8c);
          uStack_4 = 0;
          CParticleManager__CreateEffect
                    (local_74,auStack_8c,DAT_007047c8,DAT_007047cc,DAT_007047d0,DAT_007047d4,0,0);
          if ((pvStack_88 != (void *)0x0) && (iVar1 = *(int *)((int)pvStack_88 + 0xa8), iVar1 != 0))
          {
            CMCMech__Helper_004b0fb0();
            pfVar9 = *(float **)(*(int *)(*(int *)(iVar3 + 0x160) + iVar8 * 4) + 0xfc);
            fStack_84 = *pfVar9;
            fStack_80 = pfVar9[1];
            fStack_7c = pfVar9[2];
            fStack_78 = pfVar9[3];
            fStack_54 = fStack_1c * fStack_84 + fStack_18 * fStack_80 + fStack_14 * fStack_7c +
                        fStack_44;
            fStack_58 = fStack_48 +
                        fStack_2c * fStack_84 + fStack_28 * fStack_80 + fStack_24 * fStack_7c;
            fStack_5c = afStack_3c[0] * fStack_84 +
                        afStack_3c[1] * fStack_80 + afStack_3c[2] * fStack_7c + fStack_4c;
            if ((pvStack_88 != (void *)0x0) &&
               (CUnit__Helper_004097a0(pvStack_88,&fStack_5c,unaff_EDI), pvStack_88 != (void *)0x0))
            {
              pfVar9 = afStack_3c;
              pfVar10 = (float *)((int)pvStack_88 + 0x10);
              for (iVar7 = 0xc; iVar7 != 0; iVar7 = iVar7 + -1) {
                *pfVar10 = *pfVar9;
                pfVar9 = pfVar9 + 1;
                pfVar10 = pfVar10 + 1;
              }
              *(undefined4 *)((int)pvStack_88 + 0xa0) = 1;
            }
            uVar4 = _rand();
            uVar5 = _rand();
            uVar6 = _rand();
            *(int *)(iVar1 + 0x8c) = iVar3;
            *(short *)(iVar1 + 0x7e) = (short)iVar8;
            fStack_6c = (float)(int)((uVar6 & 0xff) - 0x80) * _DAT_005d908c;
            *(float *)(iVar1 + 0x48) = fStack_6c;
            fStack_68 = (float)(int)((uVar5 & 0xff) - 0x80) * _DAT_005d908c;
            *(float *)(iVar1 + 0x4c) = fStack_68;
            fVar2 = (float)(int)((uVar4 & 0xff) - 0x80) * _DAT_005d908c;
            fStack_64 = (fVar2 + fVar2) - _DAT_005d9088;
            *(float *)(iVar1 + 0x50) = fStack_64;
            *(undefined4 *)(iVar1 + 0x54) = uStack_60;
            *(undefined4 *)(iVar1 + 0x74) = *(undefined4 *)(iVar3 + 0x164);
          }
          uStack_4 = 0xffffffff;
          CParticleManager__RemoveFromGlobalList();
        }
        iVar8 = iVar8 + 1;
      } while (iVar8 < *(int *)(iVar3 + 0x15c));
    }
  }
  ExceptionList = local_c;
  return;
}
