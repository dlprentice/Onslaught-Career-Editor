/* address: 0x0040ebf0 */
/* name: CMonitor__Unk_0040ebf0 */
/* signature: void __fastcall CMonitor__Unk_0040ebf0(void * param_1) */


void __fastcall CMonitor__Unk_0040ebf0(void *param_1)

{
  undefined4 *puVar1;
  int iVar2;
  int iVar3;
  void *pvVar4;
  int iVar5;
  int *piVar6;
  undefined4 *puVar7;
  void *unaff_EDI;
  undefined4 *puVar8;
  undefined4 local_40;
  undefined4 uStack_3c;
  undefined4 uStack_38;
  undefined4 uStack_34;
  undefined4 local_30 [12];

  iVar3 = CExplosionInitThing__Helper_004725d0(0x8a9a98);
  if ((iVar3 == 0) && (DAT_008a9ac0 != 2)) {
    piVar6 = *(int **)((int)param_1 + 0x620);
    if (piVar6 == (int *)0x0) {
      pvVar4 = (void *)0x0;
    }
    else {
      pvVar4 = (void *)*piVar6;
    }
    if (pvVar4 != (void *)0x0) {
      do {
        CUnit__Helper_004cb0b0(pvVar4,0,(int)unaff_EDI);
        piVar6 = (int *)piVar6[1];
        if (piVar6 == (int *)0x0) {
          pvVar4 = (void *)0x0;
        }
        else {
          pvVar4 = (void *)*piVar6;
        }
      } while (pvVar4 != (void *)0x0);
      return;
    }
  }
  else {
    puVar1 = *(undefined4 **)((int)param_1 + 0x620);
    iVar3 = 1;
    if (puVar1 == (undefined4 *)0x0) {
      pvVar4 = (void *)0x0;
    }
    else {
      pvVar4 = (void *)*puVar1;
    }
    while (pvVar4 != (void *)0x0) {
      if (*(int *)((int)param_1 + 0x634) != *(int *)((int)param_1 + 0x630)) {
        CUnit__Helper_004cb0b0(pvVar4,0,(int)unaff_EDI);
      }
      if (*(int *)((int)param_1 + 0x630) == 0) {
        if (*(int *)((int)pvVar4 + 4) == 0) {
          CParticleManager__CreateEffect
                    (*(undefined4 *)((int)param_1 + 0x61c),pvVar4,DAT_006601e8,DAT_006601ec,
                     DAT_006601f0,DAT_006601f4,0,0);
        }
        (**(code **)(*(int *)param_1 + 0x160))(0x17,iVar3,&local_40,local_30);
        puVar7 = *(undefined4 **)((int)pvVar4 + 4);
        if (puVar7 != (undefined4 *)0x0) {
          if (puVar7[0x12] == 0x461c4000) {
            puVar7[0x20] = local_40;
            puVar7[0x21] = uStack_3c;
            puVar7[0x22] = uStack_38;
            puVar7[0x23] = uStack_34;
            puVar7[0x10] = local_40;
            puVar7[0x11] = uStack_3c;
            puVar7[0x12] = uStack_38;
            puVar7[0x13] = uStack_34;
          }
          else {
            puVar7[0x10] = *puVar7;
            puVar7[0x11] = puVar7[1];
            puVar7[0x12] = puVar7[2];
            puVar7[0x13] = puVar7[3];
          }
          CMeshRenderer__Helper_00403650(puVar7,&local_40,unaff_EDI);
        }
        iVar2 = *(int *)((int)pvVar4 + 4);
joined_r0x0040ee63:
        if (iVar2 != 0) {
          puVar7 = local_30;
          puVar8 = (undefined4 *)(iVar2 + 0x10);
          for (iVar5 = 0xc; iVar5 != 0; iVar5 = iVar5 + -1) {
            *puVar8 = *puVar7;
            puVar7 = puVar7 + 1;
            puVar8 = puVar8 + 1;
          }
          *(undefined4 *)(iVar2 + 0xa0) = 1;
        }
      }
      else if (*(int *)((int)param_1 + 0x630) == 1) {
        if (*(int *)((int)pvVar4 + 4) == 0) {
          CParticleManager__CreateEffect
                    (*(undefined4 *)((int)param_1 + 0x618),pvVar4,DAT_006601e8,DAT_006601ec,
                     DAT_006601f0,DAT_006601f4,0,0);
        }
        (**(code **)(*(int *)param_1 + 0x160))(0x17,iVar3,&local_40,local_30);
        puVar7 = *(undefined4 **)((int)pvVar4 + 4);
        if (puVar7 != (undefined4 *)0x0) {
          if (puVar7[0x12] == 0x461c4000) {
            puVar7[0x20] = local_40;
            puVar7[0x21] = uStack_3c;
            puVar7[0x22] = uStack_38;
            puVar7[0x23] = uStack_34;
            puVar7[0x10] = local_40;
            puVar7[0x11] = uStack_3c;
            puVar7[0x12] = uStack_38;
            puVar7[0x13] = uStack_34;
          }
          else {
            puVar7[0x10] = *puVar7;
            puVar7[0x11] = puVar7[1];
            puVar7[0x12] = puVar7[2];
            puVar7[0x13] = puVar7[3];
          }
          CMeshRenderer__Helper_00403650(puVar7,&local_40,unaff_EDI);
        }
        iVar2 = *(int *)((int)pvVar4 + 4);
        goto joined_r0x0040ee63;
      }
      iVar3 = iVar3 + 1;
      puVar1 = (undefined4 *)puVar1[1];
      if (puVar1 == (undefined4 *)0x0) {
        pvVar4 = (void *)0x0;
      }
      else {
        pvVar4 = (void *)*puVar1;
      }
    }
    *(undefined4 *)((int)param_1 + 0x634) = *(undefined4 *)((int)param_1 + 0x630);
  }
  return;
}
