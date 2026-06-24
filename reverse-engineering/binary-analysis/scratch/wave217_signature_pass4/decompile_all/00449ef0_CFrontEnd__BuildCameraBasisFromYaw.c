/* address: 0x00449ef0 */
/* name: CFrontEnd__BuildCameraBasisFromYaw */
/* signature: void __thiscall CFrontEnd__BuildCameraBasisFromYaw(void * this) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall CFrontEnd__BuildCameraBasisFromYaw(void *this)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  int *extraout_EAX;
  int iVar4;
  int *piVar5;
  float10 fVar6;
  float10 fVar7;
  int *in_stack_00000004;
  undefined4 *rhs_basis;
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
  rhs_basis = &local_90;
  local_48 = (float)-fVar7;
  local_3c = (float)fVar7;
  local_38 = (float)fVar6;
  (**(code **)(*in_stack_00000004 + 4))();
  uVar3 = uStack_70;
  uVar2 = uStack_74;
  uVar1 = uStack_84;
  uStack_84 = local_90;
  local_90 = uVar1;
  uStack_74 = uStack_8c;
  uStack_8c = uVar2;
  uStack_70 = uStack_7c;
  uStack_7c = uVar3;
  CMCBuggy__MultiplyMat34Basis(auStack_64,local_34,local_94,rhs_basis);
  piVar5 = extraout_EAX;
  for (iVar4 = 0xc; iVar4 != 0; iVar4 = iVar4 + -1) {
    *in_stack_00000004 = *piVar5;
    piVar5 = piVar5 + 1;
    in_stack_00000004 = in_stack_00000004 + 1;
  }
  return;
}
