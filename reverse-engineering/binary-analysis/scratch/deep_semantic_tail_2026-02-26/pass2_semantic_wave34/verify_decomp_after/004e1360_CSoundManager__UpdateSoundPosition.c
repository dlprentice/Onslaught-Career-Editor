/* address: 0x004e1360 */
/* name: CSoundManager__UpdateSoundPosition */
/* signature: void __stdcall CSoundManager__UpdateSoundPosition(void * param_1, int param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void CSoundManager__UpdateSoundPosition(void *param_1,int param_2)

{
  float fVar1;
  float fVar2;
  float fVar3;
  int *piVar4;
  undefined4 *puVar5;
  float *pfVar6;
  float *pfVar7;
  void *extraout_EAX;
  int iVar8;
  float *pfVar9;
  float10 fVar10;
  unkbyte10 Var11;
  float local_c0;
  float fStack_bc;
  float fStack_b8;
  undefined4 uStack_b4;
  undefined8 local_b0;
  float local_a8;
  undefined4 local_a4;
  float local_a0;
  float local_9c;
  float local_98;
  undefined4 local_94;
  float local_90 [4];
  float fStack_80;
  float fStack_7c;
  float fStack_78;
  float fStack_70;
  float fStack_6c;
  float fStack_68;
  undefined1 auStack_64 [4];
  float afStack_60 [12];
  float local_30 [12];

  piVar4 = CGame__GetCamera(&DAT_008a9a98,0);
  local_a4 = DAT_0083cfe4;
  local_a8 = DAT_0083cfe0;
  pfVar6 = (float *)&DAT_0083cfa8;
  pfVar7 = local_90;
  for (iVar8 = 0xc; iVar8 != 0; iVar8 = iVar8 + -1) {
    *pfVar7 = *pfVar6;
    pfVar6 = pfVar6 + 1;
    pfVar7 = pfVar7 + 1;
  }
  local_98 = DAT_0083cfe0;
  local_9c = DAT_0083cfdc;
  local_b0 = CONCAT44(DAT_0083cfdc,DAT_0083cfd8);
  local_a0 = DAT_0083cfd8;
  local_94 = DAT_0083cfe4;
  pfVar6 = (float *)&DAT_0083cfa8;
  pfVar7 = local_30;
  for (iVar8 = 0xc; iVar8 != 0; iVar8 = iVar8 + -1) {
    *pfVar7 = *pfVar6;
    pfVar6 = pfVar6 + 1;
    pfVar7 = pfVar7 + 1;
  }
  if (piVar4 != (int *)0x0) {
    puVar5 = (undefined4 *)(**(code **)*piVar4)(&local_c0);
    uStack_b4 = *puVar5;
    local_b0 = *(undefined8 *)(puVar5 + 1);
    local_a8 = (float)puVar5[3];
    pfVar6 = (float *)(**(code **)(*piVar4 + 4))(auStack_64);
    pfVar7 = local_90;
    for (iVar8 = 0xc; iVar8 != 0; iVar8 = iVar8 + -1) {
      *pfVar7 = *pfVar6;
      pfVar6 = pfVar6 + 1;
      pfVar7 = pfVar7 + 1;
    }
  }
  iVar8 = CExplosionInitThing__Helper_004725d0(0x8a9a98);
  if ((iVar8 != 0) && (piVar4 = CGame__GetCamera(&DAT_008a9a98,1), piVar4 != (int *)0x0)) {
    puVar5 = (undefined4 *)(**(code **)*piVar4)(&local_c0);
    local_a4 = *puVar5;
    local_a0 = (float)puVar5[1];
    local_9c = (float)puVar5[2];
    local_98 = (float)puVar5[3];
    pfVar6 = (float *)(**(code **)(*piVar4 + 4))(auStack_64);
    pfVar7 = local_30;
    for (iVar8 = 0xc; iVar8 != 0; iVar8 = iVar8 + -1) {
      *pfVar7 = *pfVar6;
      pfVar6 = pfVar6 + 1;
      pfVar7 = pfVar7 + 1;
    }
  }
  iVar8 = *(int *)((int)param_1 + 0x10);
  if (((iVar8 != 3) && (iVar8 != 2)) && (iVar8 != 0)) {
    if (iVar8 != 1) {
      *(undefined4 *)((int)param_1 + 0x44) = 0;
      *(undefined4 *)((int)param_1 + 0x48) = 0;
      *(undefined4 *)((int)param_1 + 0x4c) = 0;
      *(undefined4 *)((int)param_1 + 0x54) = 0;
      *(undefined4 *)((int)param_1 + 0x58) = 0;
      *(undefined4 *)((int)param_1 + 0x5c) = 0;
      iVar8 = *(int *)(*(int *)((int)param_1 + 0xc) + 4);
      if (iVar8 == 1) {
        fVar1 = *(float *)((int)param_1 + 0x44) - _DAT_005d85c0;
        *(undefined4 *)((int)param_1 + 0x48) = *(undefined4 *)((int)param_1 + 0x48);
        *(undefined4 *)((int)param_1 + 0x4c) = *(undefined4 *)((int)param_1 + 0x4c);
        *(float *)((int)param_1 + 0x44) = fVar1;
        *(undefined4 *)((int)param_1 + 0x34) = 0xffffd8f0;
      }
      else if (iVar8 == 2) {
        fVar1 = *(float *)((int)param_1 + 0x44) + _DAT_005d85c0;
        *(undefined4 *)((int)param_1 + 0x48) = *(undefined4 *)((int)param_1 + 0x48);
        *(undefined4 *)((int)param_1 + 0x4c) = *(undefined4 *)((int)param_1 + 0x4c);
        *(float *)((int)param_1 + 0x44) = fVar1;
        *(undefined4 *)((int)param_1 + 0x34) = 10000;
      }
      goto LAB_004e1752;
    }
    if (param_2 == 0) goto LAB_004e1752;
  }
  if ((*(int **)param_1 == (int *)0x0) || (*(int *)((int)param_1 + 0x80) != 0)) {
    if ((param_2 != 0) || (iVar8 == 0)) {
      *(undefined4 *)((int)param_1 + 0x44) = 0;
      *(undefined4 *)((int)param_1 + 0x48) = 0;
      *(undefined4 *)((int)param_1 + 0x4c) = 0;
      *(undefined4 *)((int)param_1 + 0x54) = 0;
      *(undefined4 *)((int)param_1 + 0x58) = 0;
      *(undefined4 *)((int)param_1 + 0x5c) = 0;
    }
  }
  else {
    pfVar6 = (float *)((int)param_1 + 0x44);
    pfVar7 = (float *)(**(code **)(**(int **)param_1 + 0xc))(&local_c0);
    *pfVar6 = *pfVar7;
    *(float *)((int)param_1 + 0x48) = pfVar7[1];
    *(float *)((int)param_1 + 0x4c) = pfVar7[2];
    *(float *)((int)param_1 + 0x50) = pfVar7[3];
    puVar5 = (undefined4 *)(**(code **)(**(int **)param_1 + 0x14))(&stack0xffffff3c);
    *(undefined4 *)((int)param_1 + 0x54) = *puVar5;
    *(undefined4 *)((int)param_1 + 0x58) = puVar5[1];
    *(undefined4 *)((int)param_1 + 0x5c) = puVar5[2];
    *(undefined4 *)((int)param_1 + 0x60) = puVar5[3];
    local_c0 = (float)local_b0;
    fStack_bc = local_b0._4_4_;
    uStack_b4 = local_a4;
    pfVar7 = local_90;
    pfVar9 = afStack_60;
    for (iVar8 = 0xc; iVar8 != 0; iVar8 = iVar8 + -1) {
      *pfVar9 = *pfVar7;
      pfVar7 = pfVar7 + 1;
      pfVar9 = pfVar9 + 1;
    }
    fStack_b8 = local_a8;
    iVar8 = CExplosionInitThing__Helper_004725d0(0x8a9a98);
    if (iVar8 != 0) {
      fVar3 = *(float *)((int)param_1 + 0x48) - local_b0._4_4_;
      fVar2 = *(float *)((int)param_1 + 0x4c) - local_a8;
      fVar1 = *(float *)((int)param_1 + 0x48) - local_9c;
      local_a8 = *(float *)((int)param_1 + 0x4c) - local_98;
      if ((*pfVar6 - local_a0) * (*pfVar6 - local_a0) + fVar1 * fVar1 + local_a8 * local_a8 <
          (*pfVar6 - (float)local_b0) * (*pfVar6 - (float)local_b0) + fVar3 * fVar3 + fVar2 * fVar2)
      {
        local_c0 = local_a0;
        fStack_b8 = local_98;
        fStack_bc = local_9c;
        uStack_b4 = local_94;
        pfVar7 = local_30;
        pfVar9 = afStack_60;
        for (iVar8 = 0xc; iVar8 != 0; iVar8 = iVar8 + -1) {
          *pfVar9 = *pfVar7;
          pfVar7 = pfVar7 + 1;
          pfVar9 = pfVar9 + 1;
        }
      }
    }
    *pfVar6 = *pfVar6 - local_c0;
    *(float *)((int)param_1 + 0x48) = *(float *)((int)param_1 + 0x48) - fStack_bc;
    *(float *)((int)param_1 + 0x4c) = *(float *)((int)param_1 + 0x4c) - fStack_b8;
    Vec3__SetXYZ();
    CMeshPart__Unk_004b0c00(afStack_60,(int)&local_a0,&local_c0);
    CMeshPart__Helper_004aa3f0(afStack_60,&local_b0,extraout_EAX);
    Mat34__SetRows();
    fVar1 = *pfVar6;
    fVar2 = *(float *)((int)param_1 + 0x48);
    fVar3 = *pfVar6;
    *pfVar6 = local_90[0] * *pfVar6 +
              local_90[2] * *(float *)((int)param_1 + 0x4c) +
              local_90[1] * *(float *)((int)param_1 + 0x48);
    *(float *)((int)param_1 + 0x48) =
         fStack_80 * fVar1 +
         fStack_78 * *(float *)((int)param_1 + 0x4c) + fStack_7c * *(float *)((int)param_1 + 0x48);
    *(float *)((int)param_1 + 0x4c) =
         fStack_70 * fVar3 + fStack_68 * *(float *)((int)param_1 + 0x4c) + fStack_6c * fVar2;
    *(undefined4 *)((int)param_1 + 0x50) = uStack_b4;
  }
LAB_004e1752:
  if (g_InvertXAxisFlag != 0) {
    *(float *)((int)param_1 + 0x44) = -*(float *)((int)param_1 + 0x44);
  }
  if (((*(int *)param_1 != 0) && (*(int *)((int)param_1 + 0x80) == 0)) &&
     ((*(int *)((int)param_1 + 0x10) == 2 || (*(int *)((int)param_1 + 0x10) == 3)))) {
    Var11 = fpatan((float10)*(float *)((int)param_1 + 0x44),(float10)*(float *)((int)param_1 + 0x48)
                  );
    fVar10 = (float10)fsin(Var11);
    fVar1 = _DAT_005d8be0;
    if ((float10)_DAT_005d856c < fVar10) {
      fVar1 = _DAT_005d8568;
    }
    fVar2 = (float)fVar10 * _DAT_005d85cc * (float)fVar10 * _DAT_005d85cc;
    local_b0._0_4_ = (float)(longlong)ROUND(fVar2 * fVar2 * fVar1);
    *(float *)((int)param_1 + 0x34) = (float)local_b0;
  }
  return;
}
