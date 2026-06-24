/* address: 0x00424a20 */
/* name: CUnitAI__Unk_00424a20 */
/* signature: void __fastcall CUnitAI__Unk_00424a20(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CUnitAI__Unk_00424a20(void *param_1)

{
  float *pfVar1;
  int iVar2;
  float fVar3;
  float fVar4;
  float fVar5;
  float fVar6;
  float fVar7;
  int iVar8;
  undefined4 *puVar9;
  undefined4 *puVar10;
  float10 fVar11;
  float local_14 [5];

  pfVar1 = (float *)((int)param_1 + 0xc);
  *(float *)((int)param_1 + 0x1c) = *pfVar1;
  *(undefined4 *)((int)param_1 + 0x20) = *(undefined4 *)((int)param_1 + 0x10);
  *(undefined4 *)((int)param_1 + 0x24) = *(undefined4 *)((int)param_1 + 0x14);
  *(undefined4 *)((int)param_1 + 0x28) = *(undefined4 *)((int)param_1 + 0x18);
  iVar2 = *(int *)((int)param_1 + 0x110);
  puVar9 = (undefined4 *)((int)param_1 + 0x2c);
  puVar10 = (undefined4 *)((int)param_1 + 0x5c);
  for (iVar8 = 0xc; iVar8 != 0; iVar8 = iVar8 + -1) {
    *puVar10 = *puVar9;
    puVar9 = puVar9 + 1;
    puVar10 = puVar10 + 1;
  }
  if ((iVar2 != 0) && ((*(byte *)(iVar2 + 0x2c) & 4) == 0)) {
    if (*(int *)(iVar2 + 0x260) == 2) {
      CUnitAI__Unk_00424ca0((int)param_1);
    }
    else {
      CUnitAI__Unk_004250f0((int)param_1);
    }
    fVar11 = (float10)fcos((float10)*(float *)((int)param_1 + 0xa0));
    local_14[1] = 0.0;
    local_14[2] = 0.0;
    local_14[3] = 0.0;
    *pfVar1 = 0.0;
    *(undefined4 *)((int)param_1 + 0x10) = 0;
    *(undefined4 *)((int)param_1 + 0x14) = 0;
    *(float *)((int)param_1 + 0x18) = local_14[4];
    *pfVar1 = (float)(fVar11 * (float10)*(float *)((int)param_1 + 0x90) + (float10)*pfVar1);
    *(float *)((int)param_1 + 0x10) =
         (float)(fVar11 * (float10)*(float *)((int)param_1 + 0x94) +
                (float10)*(float *)((int)param_1 + 0x10));
    *(float *)((int)param_1 + 0x14) =
         (float)(fVar11 * (float10)*(float *)((int)param_1 + 0x98) +
                (float10)*(float *)((int)param_1 + 0x14));
    fVar3 = *(float *)((int)param_1 + 0x90) * _DAT_005d85f8;
    *(float *)((int)param_1 + 0x90) = fVar3;
    fVar4 = *(float *)((int)param_1 + 0x94) * _DAT_005d85f8;
    *(float *)((int)param_1 + 0x94) = fVar4;
    fVar5 = *(float *)((int)param_1 + 0x98) * _DAT_005d85f8;
    fVar6 = *(float *)((int)param_1 + 0x9c) * _DAT_005d85f8;
    *(float *)((int)param_1 + 0x98) = fVar5;
    fVar7 = _DAT_005d8580;
    *(float *)((int)param_1 + 0x9c) = fVar6;
    if ((((fVar7 < ABS(fVar3)) || (_DAT_005d8580 < ABS(fVar4))) || (_DAT_005d8580 < ABS(fVar5))) ||
       (_DAT_005d8580 < ABS(fVar6))) {
      *(float *)((int)param_1 + 0xa0) = *(float *)((int)param_1 + 0xa0) + _DAT_005d85f8;
    }
    local_14[0] = -1.0;
    CEventManager__AddEvent_AtTime(&EVENT_MANAGER,0x7d1,param_1,local_14,2,(void *)0x0,(void *)0x0);
    CUnitAI__Unk_00424be0((int)param_1);
  }
  return;
}
