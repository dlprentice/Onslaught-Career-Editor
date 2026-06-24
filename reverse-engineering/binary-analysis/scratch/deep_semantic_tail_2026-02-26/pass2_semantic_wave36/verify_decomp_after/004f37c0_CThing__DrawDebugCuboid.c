/* address: 0x004f37c0 */
/* name: CThing__DrawDebugCuboid */
/* signature: void __fastcall CThing__DrawDebugCuboid(void * param_1) */


void __fastcall CThing__DrawDebugCuboid(void *param_1)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  undefined4 *puVar6;
  undefined4 *puVar7;
  float10 fVar8;
  void *pvVar9;
  float in_stack_ffffff58;
  float in_stack_ffffff5c;
  float in_stack_ffffff60;
  float in_stack_ffffff64;
  float in_stack_ffffff68;
  float in_stack_ffffff6c;
  float in_stack_ffffff70;
  float in_stack_ffffff74;
  float in_stack_ffffff78;
  float in_stack_ffffff7c;
  float in_stack_ffffff80;
  float m33;
  undefined4 uStack_60;
  undefined4 uStack_5c;
  undefined4 uStack_58;
  undefined4 uStack_50;
  undefined4 uStack_4c;
  undefined4 uStack_48;
  float fStack_40;
  float fStack_3c;
  float fStack_38;
  undefined4 local_30 [12];

  iVar4 = *(int *)((int)param_1 + 8);
  puVar6 = &DAT_0083d9f0;
  puVar7 = local_30;
  for (iVar5 = 0xc; iVar5 != 0; iVar5 = iVar5 + -1) {
    *puVar7 = *puVar6;
    puVar6 = puVar6 + 1;
    puVar7 = puVar7 + 1;
  }
  m33 = 7.275051e-39;
  iVar4 = (**(code **)(iVar4 + 0x54))();
  if (iVar4 != 0) {
    uVar2 = *(undefined4 *)(iVar4 + 0x10);
    uVar3 = *(undefined4 *)(iVar4 + 0x14);
    puVar6 = local_30;
    puVar7 = (undefined4 *)&stack0xffffff58;
    for (iVar5 = 0xc; iVar5 != 0; iVar5 = iVar5 + -1) {
      *puVar7 = *puVar6;
      puVar6 = puVar6 + 1;
      puVar7 = puVar7 + 1;
    }
    pvVar9 = *(void **)((int)param_1 + 0x28);
    CDXEngine__SetWorldMatrixElements
              (&DAT_009c65c0,*(float *)((int)param_1 + 0x1c),*(float *)((int)param_1 + 0x20),
               *(float *)((int)param_1 + 0x24),(float)pvVar9,in_stack_ffffff58,in_stack_ffffff5c,
               in_stack_ffffff60,in_stack_ffffff64,in_stack_ffffff68,in_stack_ffffff6c,
               in_stack_ffffff70,in_stack_ffffff74,in_stack_ffffff78,in_stack_ffffff7c,
               in_stack_ffffff80,m33);
    uVar1 = *(undefined4 *)(iVar4 + 0x18);
    puVar6 = local_30;
    puVar7 = (undefined4 *)&stack0xffffff54;
    m33 = DAT_0089ce88;
    uStack_50 = uVar2;
    uStack_4c = uVar3;
    for (iVar4 = 0xc; iVar4 != 0; iVar4 = iVar4 + -1) {
      *puVar7 = *puVar6;
      puVar6 = puVar6 + 1;
      puVar7 = puVar7 + 1;
    }
    uStack_60 = 0;
    uStack_5c = 0;
    uStack_58 = 0;
    uStack_48 = uVar1;
    CThing__Helper_0053d760((void *)0xff00ff00,&uStack_50,&uStack_60,pvVar9);
  }
  puVar6 = local_30;
  puVar7 = (undefined4 *)&stack0xffffff58;
  for (iVar4 = 0xc; iVar4 != 0; iVar4 = iVar4 + -1) {
    *puVar7 = *puVar6;
    puVar6 = puVar6 + 1;
    puVar7 = puVar7 + 1;
  }
  pvVar9 = *(void **)((int)param_1 + 0x28);
  CDXEngine__SetWorldMatrixElements
            (&DAT_009c65c0,*(float *)((int)param_1 + 0x1c),*(float *)((int)param_1 + 0x20),
             *(float *)((int)param_1 + 0x24),(float)pvVar9,in_stack_ffffff58,in_stack_ffffff5c,
             in_stack_ffffff60,in_stack_ffffff64,in_stack_ffffff68,in_stack_ffffff6c,
             in_stack_ffffff70,in_stack_ffffff74,in_stack_ffffff78,in_stack_ffffff7c,
             in_stack_ffffff80,m33);
  (**(code **)(*(int *)param_1 + 0x44))();
  fVar8 = (float10)(**(code **)(*(int *)param_1 + 0x40))();
  fStack_40 = (float)fVar8;
  fStack_3c = (float)fVar8;
  fStack_38 = (float)fVar8;
  puVar6 = local_30;
  puVar7 = (undefined4 *)&stack0xffffff54;
  for (iVar4 = 0xc; iVar4 != 0; iVar4 = iVar4 + -1) {
    *puVar7 = *puVar6;
    puVar6 = puVar6 + 1;
    puVar7 = puVar7 + 1;
  }
  uStack_50 = 0;
  uStack_4c = 0;
  uStack_48 = 0;
  CThing__Helper_0053d760((void *)0xffffffff,&fStack_40,&uStack_50,pvVar9);
  return;
}
