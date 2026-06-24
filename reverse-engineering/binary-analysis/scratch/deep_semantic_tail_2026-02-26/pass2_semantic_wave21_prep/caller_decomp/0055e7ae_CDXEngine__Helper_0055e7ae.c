/* address: 0x0055e7ae */
/* name: CDXEngine__Helper_0055e7ae */
/* signature: void __cdecl CDXEngine__Helper_0055e7ae(void * param_1, void * param_2, uint param_3, void * param_4) */


void __cdecl CDXEngine__Helper_0055e7ae(void *param_1,void *param_2,uint param_3,void *param_4)

{
  void *pvVar1;
  uint uVar2;
  void *pvVar3;
  int iVar4;
  void *pvVar5;
  void *pvVar6;
  undefined1 local_fc [120];
  undefined1 local_84 [120];
  void *local_c;
  int local_8;

  if ((param_2 < (void *)0x2) || (param_3 == 0)) {
    return;
  }
  local_8 = 0;
  iVar4 = (int)param_2 + -1;
  param_2 = local_fc;
  pvVar5 = (void *)(iVar4 * param_3 + (int)param_1);
  pvVar3 = param_1;
  param_1 = local_84;
LAB_0055e7ed:
  uVar2 = (uint)((int)pvVar5 - (int)pvVar3) / param_3 + 1;
  if (8 < uVar2) {
    CDXEngine__Helper_0055e950((void *)((uVar2 >> 1) * param_3 + (int)pvVar3),pvVar3,param_3);
    pvVar6 = (void *)(param_3 + (int)pvVar5);
    local_c = pvVar3;
LAB_0055e844:
    local_c = (void *)((int)local_c + param_3);
    if (local_c <= pvVar5) goto code_r0x0055e851;
    goto LAB_0055e85c;
  }
  CDXTexture__Unk_0055e902((uint)pvVar3,(uint)pvVar5,param_3,param_4);
  goto LAB_0055e80c;
code_r0x0055e851:
  iVar4 = (*param_4)(local_c,pvVar3);
  if (iVar4 < 1) goto LAB_0055e844;
LAB_0055e85c:
  do {
    pvVar6 = (void *)((int)pvVar6 - param_3);
    if (pvVar6 <= pvVar3) break;
    iVar4 = (*param_4)(pvVar6,pvVar3);
  } while (-1 < iVar4);
  if (local_c <= pvVar6) {
    CDXEngine__Helper_0055e950(local_c,pvVar6,param_3);
    goto LAB_0055e844;
  }
  CDXEngine__Helper_0055e950(pvVar3,pvVar6,param_3);
  pvVar1 = local_c;
  if ((int)pvVar6 + (-1 - (int)pvVar3) < (int)pvVar5 - (int)local_c) {
    if (local_c < pvVar5) {
      local_8 = local_8 + 1;
      *(void **)param_2 = local_c;
      *(void **)param_1 = pvVar5;
      param_1 = (void *)((int)param_1 + 4);
      param_2 = (void *)((int)param_2 + 4);
    }
    if ((void *)(param_3 + (int)pvVar3) < pvVar6) {
      pvVar5 = (void *)((int)pvVar6 - param_3);
      goto LAB_0055e7ed;
    }
  }
  else {
    if ((void *)((int)pvVar3 + param_3) < pvVar6) {
      local_8 = local_8 + 1;
      *(void **)param_2 = pvVar3;
      *(uint *)param_1 = (int)pvVar6 - param_3;
      param_1 = (void *)((int)param_1 + 4);
      param_2 = (void *)((int)param_2 + 4);
    }
    pvVar3 = pvVar1;
    if (pvVar1 < pvVar5) goto LAB_0055e7ed;
  }
LAB_0055e80c:
  local_8 = local_8 + -1;
  param_2 = (void *)((int)param_2 + -4);
  param_1 = (void *)((int)param_1 + -4);
  if (local_8 < 0) {
    return;
  }
  pvVar5 = *(void **)param_1;
  pvVar3 = *(void **)param_2;
  goto LAB_0055e7ed;
}
