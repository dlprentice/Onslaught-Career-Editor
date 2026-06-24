/* address: 0x004fc220 */
/* name: CUnit__Unk_004fc220 */
/* signature: void __fastcall CUnit__Unk_004fc220(void * param_1) */


void __fastcall CUnit__Unk_004fc220(void *param_1)

{
  int *piVar1;
  undefined4 *puVar2;
  int iVar3;
  undefined4 *puVar4;
  int iVar5;
  void *unaff_EDI;
  undefined4 local_40;
  undefined4 uStack_3c;
  undefined4 uStack_38;
  undefined4 uStack_34;
  undefined4 local_30 [12];

  if (*(int *)(*(int *)((int)param_1 + 0x164) + 0x1c) != 0) {
    piVar1 = *(int **)((int)param_1 + 0x1c4);
    if (piVar1 == (int *)0x0) {
      iVar5 = 0;
    }
    else {
      iVar5 = *piVar1;
    }
    while (iVar5 != 0) {
      (**(code **)(*(int *)param_1 + 0x160))(0x15,1,&local_40,local_30);
      *(undefined4 *)(iVar5 + 4) = 0;
      CParticleManager__CreateEffect
                (*(undefined4 *)(*(int *)((int)param_1 + 0x164) + 0x1c),iVar5,DAT_00854d80,
                 DAT_00854d84,DAT_00854d88,DAT_00854d8c,0,0);
      puVar4 = *(undefined4 **)(iVar5 + 4);
      if (puVar4 != (undefined4 *)0x0) {
        if (puVar4[0x12] == 0x461c4000) {
          puVar4[0x20] = local_40;
          puVar4[0x21] = uStack_3c;
          puVar4[0x22] = uStack_38;
          puVar4[0x23] = uStack_34;
          puVar4[0x10] = local_40;
          puVar4[0x11] = uStack_3c;
          puVar4[0x12] = uStack_38;
          puVar4[0x13] = uStack_34;
        }
        else {
          puVar4[0x10] = *puVar4;
          puVar4[0x11] = puVar4[1];
          puVar4[0x12] = puVar4[2];
          puVar4[0x13] = puVar4[3];
        }
        CMeshRenderer__Helper_00403650(puVar4,&local_40,unaff_EDI);
      }
      iVar5 = *(int *)(iVar5 + 4);
      if (iVar5 != 0) {
        puVar4 = local_30;
        puVar2 = (undefined4 *)(iVar5 + 0x10);
        for (iVar3 = 0xc; iVar3 != 0; iVar3 = iVar3 + -1) {
          *puVar2 = *puVar4;
          puVar4 = puVar4 + 1;
          puVar2 = puVar2 + 1;
        }
        *(undefined4 *)(iVar5 + 0xa0) = 1;
      }
      piVar1 = (int *)piVar1[1];
      if (piVar1 == (int *)0x0) {
        iVar5 = 0;
      }
      else {
        iVar5 = *piVar1;
      }
    }
  }
  puVar4 = *(undefined4 **)((int)param_1 + 0x19c);
  if (puVar4 == (undefined4 *)0x0) {
    puVar2 = (undefined4 *)0x0;
  }
  else {
    puVar2 = (undefined4 *)*puVar4;
  }
  while (puVar2 != (undefined4 *)0x0) {
    if ((void *)*puVar2 != (void *)0x0) {
      CUnit__Unk_004fc220((void *)*puVar2);
    }
    puVar4 = (undefined4 *)puVar4[1];
    if (puVar4 == (undefined4 *)0x0) {
      puVar2 = (undefined4 *)0x0;
    }
    else {
      puVar2 = (undefined4 *)*puVar4;
    }
  }
  return;
}
