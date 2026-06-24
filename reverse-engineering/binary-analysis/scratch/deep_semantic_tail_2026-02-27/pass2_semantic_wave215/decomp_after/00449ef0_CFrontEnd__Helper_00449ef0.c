/* address: 0x00449ef0 */
/* name: CFrontEnd__Helper_00449ef0 */
/* signature: void __stdcall CFrontEnd__Helper_00449ef0(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void CFrontEnd__Helper_00449ef0(void *param_1)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  undefined4 *extraout_EAX;
  int iVar4;
  undefined4 *puVar5;
  float10 fVar6;
  float10 fVar7;
  undefined1 local_94 [4];
  undefined4 local_90;
  undefined4 uStack_8c;
  undefined4 uStack_84;
  undefined4 uStack_7c;
  undefined4 uStack_74;
  undefined4 uStack_70;
  undefined1 auStack_64 [4];
  undefined4 local_60;
  undefined4 local_5c;
  undefined4 local_58;
  undefined4 local_50;
  float local_4c;
  float local_48;
  undefined4 local_40;
  float local_3c;
  float local_38;
  undefined1 local_34 [52];

  fVar6 = (float10)fcos((float10)_DAT_005db280);
  local_5c = 0;
  local_60 = 0x3f800000;
  local_58 = 0;
  local_50 = 0;
  local_4c = (float)fVar6;
  fVar7 = (float10)fsin((float10)_DAT_005db280);
  local_40 = 0;
  puVar5 = &local_90;
  local_48 = (float)-fVar7;
  local_3c = (float)fVar7;
  local_38 = (float)fVar6;
  (**(code **)(*(int *)param_1 + 4))();
  uVar3 = uStack_70;
  uVar2 = uStack_74;
  uVar1 = uStack_84;
  uStack_84 = local_90;
  local_90 = uVar1;
  uStack_74 = uStack_8c;
  uStack_8c = uVar2;
  uStack_70 = uStack_7c;
  uStack_7c = uVar3;
  CMCBuggy__Helper_0040d320(auStack_64,local_34,local_94,puVar5);
  puVar5 = extraout_EAX;
  for (iVar4 = 0xc; iVar4 != 0; iVar4 = iVar4 + -1) {
    *(undefined4 *)param_1 = *puVar5;
    puVar5 = puVar5 + 1;
    param_1 = (undefined4 *)((int)param_1 + 4);
  }
  return;
}
