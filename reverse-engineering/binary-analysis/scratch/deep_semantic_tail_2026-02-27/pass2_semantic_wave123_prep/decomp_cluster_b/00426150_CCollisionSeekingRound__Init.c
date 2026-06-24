/* address: 0x00426150 */
/* name: CCollisionSeekingRound__Init */
/* signature: undefined CCollisionSeekingRound__Init(void) */


void __thiscall CCollisionSeekingRound__Init(int param_1,undefined4 *param_2)

{
  float fVar1;
  float fVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  undefined4 uVar6;
  undefined4 uVar7;
  uint uVar8;
  undefined4 *puVar9;
  void *unaff_EDI;
  float10 fVar10;
  undefined4 uStack_14;
  float fStack_10;
  float fStack_c;
  float fStack_8;

  *(undefined4 *)(param_1 + 8) = *param_2;
  *(undefined4 *)(param_1 + 0xc) = 0;
  uVar8 = param_2[4];
  *(uint *)(param_1 + 0xc) = uVar8;
  uVar8 = param_2[5] << 2 | uVar8;
  *(uint *)(param_1 + 0xc) = uVar8;
  uVar8 = param_2[6] << 4 | uVar8;
  *(uint *)(param_1 + 0xc) = uVar8;
  uVar8 = (param_2[7] | 0x10) << 6 | uVar8;
  *(uint *)(param_1 + 0xc) = uVar8;
  *(uint *)(param_1 + 0xc) = param_2[10] << 9 | uVar8;
  *(undefined4 *)(param_1 + 0x20) = param_2[1];
  uVar3 = param_2[2];
  *(undefined4 *)(param_1 + 0x18) = 0;
  *(undefined4 *)(param_1 + 0x10) = uVar3;
  fVar10 = (float10)(**(code **)(**(int **)(param_1 + 8) + 0x44))();
  fVar1 = (float)fVar10;
  if (param_2[3] == 0) {
    puVar9 = (undefined4 *)
             OID__AllocObject(0x1c,0x5c,s_C__dev_ONSLAUGHT2_collisionseeki_006246d8,0x28);
    if (puVar9 == (undefined4 *)0x0) {
      *(undefined4 *)(param_1 + 0x14) = 0;
      *(float *)(param_1 + 0x1c) = fVar1;
    }
    else {
      puVar9[1] = 0;
      puVar9[2] = 0;
      puVar9[3] = 0;
      puVar9[5] = fVar1;
      puVar9[6] = fVar1 * fVar1;
      *puVar9 = &PTR_VFuncSlot_00_00426340_005d95e8;
      *(undefined4 **)(param_1 + 0x14) = puVar9;
      *(float *)(param_1 + 0x1c) = fVar1;
    }
  }
  else {
    *(undefined4 *)(param_1 + 0x14) = param_2[3];
    *(float *)(param_1 + 0x1c) = fVar1;
  }
  CUnitAI__Helper_004f3ac0(*(void **)(param_1 + 8),(int)&fStack_10,unaff_EDI);
  iVar4 = *(int *)(param_1 + 8);
  iVar5 = *(int *)(param_1 + 0x14);
  fVar1 = *(float *)(iVar4 + 0x20);
  fVar2 = *(float *)(iVar4 + 0x24);
  *(float *)(iVar5 + 4) = fStack_10 - *(float *)(iVar4 + 0x1c);
  *(float *)(iVar5 + 8) = fStack_c - fVar1;
  *(float *)(iVar5 + 0xc) = fStack_8 - fVar2;
  *(undefined4 *)(iVar5 + 0x10) = uStack_14;
  if (((byte)*(undefined4 *)(param_1 + 0xc) & 0x30) == 0x20) {
    puVar9 = (undefined4 *)
             OID__AllocObject(0x28,0x5c,s_C__dev_ONSLAUGHT2_collisionseeki_006246d8,0x39);
    if (puVar9 != (undefined4 *)0x0) {
      uVar3 = param_2[0xc];
      uVar6 = param_2[9];
      uVar7 = *(undefined4 *)(*(int *)(param_1 + 8) + 0x30);
      puVar9[1] = 0;
      puVar9[2] = 0;
      puVar9[3] = 0;
      puVar9[5] = uVar7;
      puVar9[6] = 0;
      puVar9[7] = uVar3;
      puVar9[8] = uVar6;
      puVar9[9] = 0;
      *puVar9 = &PTR_CMeshCollisionVolume__VFunc_00_00426300_005d95c8;
      *(undefined4 **)(param_1 + 0x18) = puVar9;
      return;
    }
    *(undefined4 *)(param_1 + 0x18) = 0;
  }
  return;
}
