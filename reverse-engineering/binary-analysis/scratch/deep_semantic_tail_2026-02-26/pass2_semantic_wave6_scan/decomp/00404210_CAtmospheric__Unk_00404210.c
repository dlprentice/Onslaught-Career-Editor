/* address: 0x00404210 */
/* name: CAtmospheric__Unk_00404210 */
/* signature: void __fastcall CAtmospheric__Unk_00404210(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CAtmospheric__Unk_00404210(void *param_1)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  float fVar5;
  void *pvVar6;
  int iVar7;
  void *pvVar8;
  int iVar9;
  float *pfVar10;
  float *pfVar11;
  float10 extraout_ST0;
  float10 fVar12;
  float10 fVar13;
  float local_28;
  float local_1c;
  float local_14;
  float local_10;
  float local_c;
  float local_8;
  undefined4 local_4;

  *(undefined4 *)((int)param_1 + 0x8c) = *(undefined4 *)((int)param_1 + 0x1c);
  *(undefined4 *)((int)param_1 + 0x90) = *(undefined4 *)((int)param_1 + 0x20);
  *(undefined4 *)((int)param_1 + 0x94) = *(undefined4 *)((int)param_1 + 0x24);
  *(undefined4 *)((int)param_1 + 0x98) = *(undefined4 *)((int)param_1 + 0x28);
  iVar7 = *(int *)((int)param_1 + 0xd0);
  pfVar10 = (float *)((int)param_1 + 0x3c);
  pfVar11 = (float *)((int)param_1 + 0x9c);
  for (iVar9 = 0xc; iVar9 != 0; iVar9 = iVar9 + -1) {
    *pfVar11 = *pfVar10;
    pfVar10 = pfVar10 + 1;
    pfVar11 = pfVar11 + 1;
  }
  if ((iVar7 == 0) || (iVar7 = _rand(), iVar7 % 0x32 == 1)) {
    iVar7 = _rand();
    iVar7 = iVar7 % DAT_00660134;
    for (pvVar6 = DAT_00660130;
        (pvVar8 = pvVar6, 0 < iVar7 && (pvVar8 = (void *)0x0, pvVar6 != (void *)0x0));
        pvVar6 = *(void **)((int)pvVar6 + 0xcc)) {
      iVar7 = iVar7 + -1;
    }
    if (pvVar8 != param_1) {
      *(void **)((int)param_1 + 0xd0) = pvVar8;
    }
  }
  iVar7 = *(int *)((int)param_1 + 0xd0);
  if (iVar7 == 0) goto LAB_0040458c;
  local_10 = *(float *)((int)param_1 + 0x40);
  local_c = *(float *)((int)param_1 + 0x50);
  local_8 = *(float *)((int)param_1 + 0x60);
  local_4 = *(undefined4 *)(iVar7 + 0x28);
  fVar13 = (float10)fpatan((float10)*(float *)(iVar7 + 0x1c) -
                           (float10)*(float *)((int)param_1 + 0x1c),
                           (float10)*(float *)(iVar7 + 0x20) -
                           (float10)*(float *)((int)param_1 + 0x20));
  local_28 = (float)-fVar13;
  fVar13 = (float10)fpatan((float10)local_10,(float10)local_c);
  fVar1 = (float)-fVar13;
  local_14 = SQRT(local_10 * local_10 + local_c * local_c + local_8 * local_8);
  if (local_14 <= _DAT_005d856c) {
    local_1c = 0.0;
  }
  else {
    OID__Helper_0055dcb0();
    local_1c = (float)extraout_ST0;
  }
  Vec3__SetXYZ();
  Vec3__SetXYZ();
  fVar2 = ABS(local_28 - fVar1);
  if (_DAT_005d87c0 <= fVar2) {
    if (local_28 <= fVar1) {
      if (fVar2 <= _DAT_005d85e8) goto LAB_004043c5;
      local_28 = fVar1 + _DAT_005d87c0;
    }
    else if (_DAT_005d85e8 < fVar2) {
LAB_004043c5:
      local_28 = fVar1 - _DAT_005d87c0;
    }
    else {
      local_28 = fVar1 + _DAT_005d87c0;
    }
  }
  iVar7 = _rand();
  if (iVar7 % 100 == 0) {
    iVar7 = _rand();
    *(float *)((int)param_1 + 0xdc) = (float)iVar7 * _DAT_005d85ec * _DAT_005d8618 - _DAT_005d858c;
  }
  if (_DAT_005d87bc < *(float *)((int)param_1 + 0x24)) {
    *(undefined4 *)((int)param_1 + 0xdc) = 0xbe800000;
  }
  if (*(float *)((int)param_1 + 0x24) < _DAT_005d87b8) {
    *(undefined4 *)((int)param_1 + 0xdc) = 0x3e800000;
  }
  fVar13 = (float10)local_1c;
  if ((float10)*(float *)((int)param_1 + 0xdc) < fVar13) {
    fVar13 = fVar13 - (float10)_DAT_005d8574;
  }
  if (fVar13 < (float10)*(float *)((int)param_1 + 0xdc)) {
    fVar13 = fVar13 + (float10)_DAT_005d8574;
  }
  fVar12 = (float10)fcos((float10)local_28);
  fVar1 = (float)fVar12;
  fVar12 = (float10)fsin((float10)local_28);
  fVar2 = (float)fVar12;
  fVar12 = (float10)fcos((float10)_DAT_005d87b0);
  fVar3 = (float)fVar12;
  fVar12 = (float10)fsin((float10)_DAT_005d87b0);
  fVar4 = (float)fVar12;
  fVar12 = (float10)fcos(fVar13);
  fVar5 = (float)fVar12;
  fVar13 = (float10)fsin(fVar13);
  *(float *)((int)param_1 + 0x3c) =
       (float)((float10)fVar3 * (float10)fVar1 - fVar13 * (float10)fVar4 * (float10)fVar2);
  *(float *)((int)param_1 + 0x40) = -(fVar5 * fVar2);
  local_14 = (float)(fVar13 * (float10)fVar3);
  *(float *)((int)param_1 + 0x44) = local_14 * fVar2 + fVar4 * fVar1;
  *(float *)((int)param_1 + 0x4c) =
       (float)(fVar13 * (float10)fVar4 * (float10)fVar1 + (float10)fVar3 * (float10)fVar2);
  *(float *)((int)param_1 + 0x50) = fVar5 * fVar1;
  *(float *)((int)param_1 + 0x54) = fVar4 * fVar2 - local_14 * fVar1;
  *(float *)((int)param_1 + 0x5c) = -(fVar5 * fVar4);
  *(float *)((int)param_1 + 0x60) = (float)fVar13;
  *(float *)((int)param_1 + 100) = fVar5 * fVar3;
  local_10 = *(float *)((int)param_1 + 0x40) * _DAT_005d87c0;
  local_c = *(float *)((int)param_1 + 0x50) * _DAT_005d87c0;
  local_8 = *(float *)((int)param_1 + 0x60) * _DAT_005d87c0;
  *(float *)((int)param_1 + 0x7c) = local_10;
  *(float *)((int)param_1 + 0x80) = local_c;
  *(float *)((int)param_1 + 0x84) = local_8;
  *(undefined4 *)((int)param_1 + 0x88) = local_4;
  *(float *)((int)param_1 + 0x1c) =
       *(float *)((int)param_1 + 0x1c) + *(float *)((int)param_1 + 0x7c);
  *(float *)((int)param_1 + 0x20) =
       *(float *)((int)param_1 + 0x80) + *(float *)((int)param_1 + 0x20);
  *(float *)((int)param_1 + 0x24) =
       *(float *)((int)param_1 + 0x84) + *(float *)((int)param_1 + 0x24);
LAB_0040458c:
  CMapWhoEntry__UpdatePosition((int)param_1 + 0x1c);
  if ((*(byte *)((int)param_1 + 0x2c) & 1) == 0) {
    local_14 = -1.0;
    CEventManager__AddEvent_AtTime(&EVENT_MANAGER,3000,param_1,&local_14,0,(void *)0x0,(void *)0x0);
  }
  return;
}
