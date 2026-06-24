/* address: 0x004015e0 */
/* name: CUnit__IntegrateVelocityAndResolveGroundCollision */
/* signature: void __fastcall CUnit__IntegrateVelocityAndResolveGroundCollision(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CUnit__IntegrateVelocityAndResolveGroundCollision(void *param_1)

{
  float *pfVar1;
  float fVar2;
  float fVar3;
  int iVar4;
  undefined4 *puVar5;
  undefined4 *puVar6;
  float10 fVar7;
  float10 fVar8;
  float10 fVar9;
  double dVar10;
  undefined2 local_28;
  undefined2 local_26;
  undefined4 local_24;
  float fStack_20;
  float fStack_1c;
  float fStack_18;
  float fStack_10;
  float fStack_c;

  pfVar1 = (float *)((int)param_1 + 0x1c);
  *(undefined4 *)((int)param_1 + 0xd8) = DAT_00672fd0;
  *(float *)((int)param_1 + 0x8c) = *pfVar1;
  *(undefined4 *)((int)param_1 + 0x90) = *(undefined4 *)((int)param_1 + 0x20);
  *(undefined4 *)((int)param_1 + 0x94) = *(undefined4 *)((int)param_1 + 0x24);
  *(undefined4 *)((int)param_1 + 0x98) = *(undefined4 *)((int)param_1 + 0x28);
  puVar5 = (undefined4 *)((int)param_1 + 0x3c);
  puVar6 = (undefined4 *)((int)param_1 + 0x9c);
  for (iVar4 = 0xc; iVar4 != 0; iVar4 = iVar4 + -1) {
    *puVar6 = *puVar5;
    puVar5 = puVar5 + 1;
    puVar6 = puVar6 + 1;
  }
  if ((*(int *)((int)param_1 + 0x18) != -1) && (param_1 != (void *)0xfffffff4)) {
    local_28 = *(undefined2 *)((int)param_1 + 0x14);
    local_26 = *(undefined2 *)((int)param_1 + 0x16);
    local_24 = *(undefined4 *)((int)param_1 + 0x18);
  }
  if (DAT_00662dd0 != 0) {
    if ((*(byte *)((int)param_1 + 0x34) & 0x10) == 0) {
      fVar3 = SQRT(*(float *)((int)param_1 + 0x84) * *(float *)((int)param_1 + 0x84) +
                   *(float *)((int)param_1 + 0x80) * *(float *)((int)param_1 + 0x80) +
                   *(float *)((int)param_1 + 0x7c) * *(float *)((int)param_1 + 0x7c));
      fVar7 = (float10)(**(code **)(*(int *)param_1 + 0x3c))();
      fVar9 = (float10)_DAT_005d8584;
      if ((float10)fVar3 <= fVar7 * fVar9 + (float10)_DAT_005d8580) goto LAB_00401757;
      fVar8 = (float10)(**(code **)(*(int *)param_1 + 0x3c))();
      (**(code **)(*(int *)param_1 + 0x1c))
                ((double)((fVar3 - (float)(fVar7 * fVar9)) * _DAT_005d857c),(double)fVar8);
    }
    else {
      fVar3 = SQRT(*(float *)((int)param_1 + 0x80) * *(float *)((int)param_1 + 0x80) +
                   *(float *)((int)param_1 + 0x7c) * *(float *)((int)param_1 + 0x7c));
      fVar7 = (float10)(**(code **)(*(int *)param_1 + 0x3c))();
      fVar9 = (float10)_DAT_005d8584;
      if ((float10)fVar3 <= fVar7 * fVar9 + (float10)_DAT_005d8580) goto LAB_00401757;
      fVar8 = (float10)(**(code **)(*(int *)param_1 + 0x3c))();
      (**(code **)(*(int *)param_1 + 0x1c))
                ((double)((fVar3 - (float)(fVar7 * fVar9)) * _DAT_005d857c),(double)fVar8);
    }
    CConsole__Printf(&DAT_0066f580,s_Warning_object__s_travling_beyon_00622c68);
  }
LAB_00401757:
  *pfVar1 = *pfVar1 + *(float *)((int)param_1 + 0x7c);
  *(float *)((int)param_1 + 0x20) =
       *(float *)((int)param_1 + 0x80) + *(float *)((int)param_1 + 0x20);
  *(float *)((int)param_1 + 0x24) =
       *(float *)((int)param_1 + 0x84) + *(float *)((int)param_1 + 0x24);
  fVar3 = DAT_006fbdfc;
  fVar9 = (float10)(**(code **)(*(int *)param_1 + 0xc0))();
  iVar4 = (**(code **)(*(int *)param_1 + 0xb0))();
  if (iVar4 != 0) {
    dVar10 = CStaticShadows__Helper_0047eb80(0x6fadc8,pfVar1);
    fVar7 = (float10)(**(code **)(*(int *)param_1 + 0xc0))();
    if ((float10)(float)dVar10 - fVar7 <= (float10)*(float *)((int)param_1 + 0x24)) {
      *(float *)((int)param_1 + 0x24) = (float)((float10)(float)dVar10 - fVar7);
      if ((*(byte *)((int)param_1 + 0x2c) & 0x80) == 0) {
        (**(code **)(*(int *)param_1 + 0x110))();
        fVar2 = *(float *)((int)param_1 + 0x84);
        fVar7 = (float10)(**(code **)(*(int *)param_1 + 0xb4))();
        if ((float10)ABS(fVar2) <= fVar7 + (float10)_DAT_005d8578) {
          *(undefined4 *)((int)param_1 + 0x84) = 0;
        }
        else {
          fVar7 = (float10)(**(code **)(*(int *)param_1 + 0xbc))();
          *(float *)((int)param_1 + 0x84) =
               (float)-(fVar7 * (float10)*(float *)((int)param_1 + 0x84));
        }
      }
      else {
        CMonitor__Helper_0047ec60(0x6fadc8,&fStack_20,pfVar1);
        fVar2 = fStack_20 * *(float *)((int)param_1 + 0x7c) +
                fStack_1c * *(float *)((int)param_1 + 0x80) +
                fStack_18 * *(float *)((int)param_1 + 0x84);
        fStack_10 = fStack_20 * fVar2;
        fStack_c = fStack_1c * fVar2;
        *(float *)((int)param_1 + 0x7c) = *(float *)((int)param_1 + 0x7c) - fStack_10;
        *(float *)((int)param_1 + 0x80) = *(float *)((int)param_1 + 0x80) - fStack_c;
        *(float *)((int)param_1 + 0x84) = *(float *)((int)param_1 + 0x84) - fVar2 * fStack_18;
      }
    }
    if ((float)((float10)fVar3 - fVar9) <= *(float *)((int)param_1 + 0x24)) {
      (**(code **)(*(int *)param_1 + 0x114))();
    }
  }
  if ((((*(int *)((int)param_1 + 0x18) != -1) && (param_1 != (void *)0xfffffff4)) &&
      (iVar4 = CMapWhoEntry__UpdatePosition(), iVar4 != 0)) &&
     (*(int **)((int)param_1 + 0x38) != (int *)0x0)) {
    (**(code **)(**(int **)((int)param_1 + 0x38) + 0x14))(&local_28,(int)param_1 + 0x14);
  }
  return;
}
