/* address: 0x004db150 */
/* name: CEngine__SpawnConfiguredProjectile */
/* signature: void __fastcall CEngine__SpawnConfiguredProjectile(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CEngine__SpawnConfiguredProjectile(int param_1)

{
  float fVar1;
  float fVar2;
  float fVar3;
  int *to_read;
  uint uVar4;
  int *item;
  int iVar5;
  undefined4 *puVar6;
  float unaff_EDI;
  undefined4 *puVar7;
  float10 extraout_ST0;
  float10 fVar8;
  double dVar9;
  float local_458;
  float local_444;
  float local_440;
  float local_43c;
  undefined4 local_438;
  int *local_434;
  void *local_430;
  float local_42c;
  float local_428;
  float local_424;
  float local_418;
  undefined4 local_40c [12];
  undefined **local_3dc;
  float local_3d8;
  float local_3d4;
  float local_3d0;
  undefined4 local_3cc;
  undefined4 local_3c8 [15];
  float local_38c;
  float local_388;
  float local_384;
  undefined4 local_37c;
  float local_20;
  float local_1c;
  float local_18;
  undefined4 local_14;
  int local_10;
  int local_c;
  undefined4 local_8;
  float local_4;

  local_434 = (int *)CEngine__Helper_004daba0(param_1);
  if (local_434 == (int *)0x0) {
    uVar4 = Random__NextLCGAbs(DAT_008a9d9c);
    uVar4 = uVar4 & 0x8000ffff;
    if ((int)uVar4 < 0) {
      uVar4 = (uVar4 - 1 | 0xffff0000) + 1;
    }
    local_444 = ((float)(int)uVar4 * _DAT_005d8d54 - _DAT_005d85ec) *
                *(float *)(*(int *)(param_1 + 0xf0) + 0x90) + *(float *)(param_1 + 0x1c);
    uVar4 = Random__NextLCGAbs(DAT_008a9d9c);
    uVar4 = uVar4 & 0x8000ffff;
    if ((int)uVar4 < 0) {
      uVar4 = (uVar4 - 1 | 0xffff0000) + 1;
    }
    local_440 = ((float)(int)uVar4 * _DAT_005d8d54 - _DAT_005d85ec) *
                *(float *)(*(int *)(param_1 + 0xf0) + 0x90) + *(float *)(param_1 + 0x20);
    dVar9 = CStaticShadows__Helper_0047eb80(0x6fadc8,&local_444);
    local_43c = (float)dVar9 + _DAT_005d85ec;
  }
  else {
    (**(code **)(*local_434 + 0x168))(&local_444);
  }
  item = (int *)CWorldPhysicsManager__CreateProjectile(*(undefined4 *)(param_1 + 0xf0));
  if (item != (int *)0x0) {
    CInfluenceMap__Init();
    local_20 = -1.0;
    local_1c = -1.0;
    local_10 = *(int *)(param_1 + 0x118) + 1;
    local_3dc = &PTR_VFuncSlot_00_0040e1b0_005de9b4;
    local_18 = -1.0;
    local_c = 0;
    local_8 = 0;
    local_4 = 0.0;
    if (*(int *)(item[0x3c] + 0x50) == 0) {
      local_418 = *(float *)(item[0x3c] + 0x2c) * _DAT_005d8584;
    }
    else {
      fVar1 = local_444 - *(float *)(param_1 + 0x1c);
      fVar3 = local_440 - *(float *)(param_1 + 0x20);
      fVar2 = local_43c - *(float *)(param_1 + 0x24);
      local_418 = SQRT(fVar1 * fVar1 + fVar3 * fVar3 + fVar2 * fVar2);
    }
    local_3d8 = *(float *)(param_1 + 0x1c);
    local_3d4 = *(float *)(param_1 + 0x20);
    local_3d0 = *(float *)(param_1 + 0x24);
    local_3cc = *(undefined4 *)(param_1 + 0x28);
    dVar9 = CStaticShadows__Helper_0047eb80(0x6fadc8,(float *)(param_1 + 0x1c));
    if ((float)dVar9 - _DAT_005d8568 < local_3d0) {
      local_3d0 = (float)dVar9 - _DAT_005d8568;
    }
    fVar1 = local_444 - local_3d8;
    local_18 = local_43c;
    fVar2 = local_440 - local_3d4;
    local_20 = local_444;
    local_1c = local_440;
    local_14 = local_438;
    fVar3 = local_43c - local_3d0;
    if (SQRT(fVar1 * fVar1 + fVar3 * fVar3 + fVar2 * fVar2) <= _DAT_005d856c) {
      local_458 = 0.0;
    }
    else {
      OID__Helper_0055dcb0();
      local_458 = (float)extraout_ST0;
    }
    fVar8 = (float10)fpatan((float10)fVar1,(float10)fVar2);
    local_430 = (void *)(float)-fVar8;
    CSquadNormal__Helper_004062d0(local_40c,local_430,local_458,0.0,unaff_EDI);
    puVar6 = local_40c;
    puVar7 = local_3c8;
    for (iVar5 = 0xc; iVar5 != 0; iVar5 = iVar5 + -1) {
      *puVar7 = *puVar6;
      puVar6 = puVar6 + 1;
      puVar7 = puVar7 + 1;
    }
    Vec3__SetXYZ();
    local_c = *(int *)(param_1 + 0xf0);
    local_37c = 1;
    local_4 = *(float *)(local_c + 0x24);
    local_8 = *(undefined4 *)(local_c + 0x94);
    local_38c = fVar1;
    local_388 = fVar2;
    local_384 = fVar3;
    CGenericActiveReader__SetReader(item + 0x3b,*(void **)(param_1 + 0xec));
    to_read = local_434;
    if ((local_434 != (int *)0x0) &&
       ((*(int *)(item[0x3c] + 0x48) != 0 || (*(float *)(item[0x3c] + 0x1c) < _DAT_005d856c)))) {
      CRound__Helper_004dab50(item);
      CGenericActiveReader__SetReader(item + 0x3a,to_read);
      if ((*(byte *)(to_read + 0xd) & 8) != 0) {
        CSPtrSet__AddToHead(&DAT_008551a0,item);
      }
    }
    Vec3__SetXYZ();
    fVar1 = local_424 * local_424 + local_428 * local_428 + local_42c * local_42c;
    if (fVar1 < local_4 * local_418) {
      fVar1 = SQRT(fVar1);
      uVar4 = Random__NextLCGAbs(DAT_008a9d9c);
      local_434 = (int *)(uVar4 & 0x8000ffff);
      fVar2 = *(float *)(item[0x3c] + 0x7c) * fVar1;
      if ((int)local_434 < 0) {
        local_434 = (int *)(((int)local_434 - 1U | 0xffff0000) + 1);
      }
      fVar3 = (float)(int)local_434 * _DAT_005de9ac * _DAT_005d85fc * fVar2;
      local_4 = (((fVar3 + fVar3) - fVar2) + fVar1) / local_418;
    }
    (**(code **)(*item + 0x24))(&local_3dc);
  }
  return;
}
