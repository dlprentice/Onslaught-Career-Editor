/* address: 0x00428800 */
/* name: CUnitAI__HandleTriggerEventAndMoveToOffset */
/* signature: int __fastcall CUnitAI__HandleTriggerEventAndMoveToOffset(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __fastcall CUnitAI__HandleTriggerEventAndMoveToOffset(void *param_1)

{
  int *piVar1;
  float fVar2;
  int iVar3;
  float *pfVar4;
  float local_54;
  float fStack_50;
  float local_4c;
  undefined4 local_48;
  float fStack_44;
  float local_40;
  float local_3c;
  float local_38;
  float fStack_34;
  float local_30;
  float local_2c;
  float local_28;
  float fStack_24;
  float fStack_20;
  float fStack_1c;
  undefined1 local_10 [16];

  if ((*(int *)(*(int *)((int)param_1 + 0x164) + 0x124) == 0) &&
     (*(int *)(*(int *)((int)param_1 + 0x164) + 0x198) == 0)) {
    iVar3 = CUnit__Helper_004fd140((int)param_1);
    if (iVar3 != 0) {
      CUnit__Unk_004fd040(param_1);
      return 1;
    }
  }
  else {
    iVar3 = CUnit__Helper_004fd140((int)param_1);
    if (iVar3 != 0) {
      CUnit__Unk_004fcfe0((int)param_1);
      if (*(int *)(*(int *)((int)param_1 + 0x164) + 0x198) == 0) {
        local_54 = DAT_00672fd0 + _DAT_005d8c48;
        CEventManager__AddEvent_AtTime
                  (&EVENT_MANAGER,0xfa4,param_1,&local_54,0,(void *)0x0,(void *)0x0);
        return 1;
      }
      piVar1 = *(int **)((int)param_1 + 0x26c);
      local_40 = *(float *)((int)param_1 + 0x1c) - (float)piVar1[7];
      local_4c = *(float *)((int)param_1 + 0x20) - (float)piVar1[8];
      fVar2 = SQRT(local_40 * local_40 + local_4c * local_4c);
      if (fVar2 != _DAT_005d856c) {
        fVar2 = _DAT_005d8568 / fVar2;
        local_40 = local_40 * fVar2;
        local_4c = local_4c * fVar2;
      }
      local_48 = 0;
      local_30 = (float)piVar1[0x10] * _DAT_005d8c40;
      local_2c = (float)piVar1[0x14] * _DAT_005d8c40;
      local_28 = (float)piVar1[0x18] * _DAT_005d8c40;
      local_40 = local_40 * _DAT_005d8c40;
      local_3c = local_4c * _DAT_005d8c40;
      local_38 = _DAT_005d8c40 * 0.0;
      pfVar4 = (float *)(**(code **)(*piVar1 + 0x6c))(local_10);
      fStack_50 = local_40 + pfVar4[1];
      local_4c = local_3c + pfVar4[2];
      fStack_24 = fStack_44 + *pfVar4 + fStack_34;
      fStack_20 = fStack_50 + local_30;
      fStack_1c = local_4c + local_2c;
      (**(code **)(*(int *)param_1 + 0x70))(&fStack_24);
      return 1;
    }
  }
  return 0;
}
