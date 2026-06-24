/* address: 0x0040e940 */
/* name: CMonitor__Unk_0040e940 */
/* signature: void __fastcall CMonitor__Unk_0040e940(void * param_1) */


void __fastcall CMonitor__Unk_0040e940(void *param_1)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  undefined4 *puVar4;
  undefined4 *puVar5;
  int local_44;
  undefined4 local_40;
  undefined4 uStack_3c;
  undefined4 uStack_38;
  undefined4 uStack_34;
  undefined4 local_30 [12];

  iVar2 = CExplosionInitThing__Helper_004725d0(0x8a9a98);
  if (iVar2 != 0) {
    piVar1 = *(int **)((int)param_1 + 0x1d4);
    local_44 = 1;
    if (piVar1 == (int *)0x0) {
      iVar2 = 0;
    }
    else {
      iVar2 = *piVar1;
    }
    while (iVar2 != 0) {
      if (*(int *)(iVar2 + 4) == 0) {
        CParticleManager__CreateEffect
                  (*(undefined4 *)((int)param_1 + 0x614),iVar2,DAT_006601e8,DAT_006601ec,
                   DAT_006601f0,DAT_006601f4,0,0);
      }
      (**(code **)(*(int *)param_1 + 0x160))(0x1a,local_44,&local_40,local_30);
      puVar4 = *(undefined4 **)(iVar2 + 4);
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
          *puVar4 = local_40;
          puVar4[1] = uStack_3c;
          puVar4[2] = uStack_38;
          puVar4[3] = uStack_34;
          if (puVar4[0x2b] != -0x40800000) {
            puVar4[0x2b] = DAT_00672fd0;
          }
        }
        else {
          puVar4[0x10] = *puVar4;
          puVar4[0x11] = puVar4[1];
          puVar4[0x12] = puVar4[2];
          puVar4[0x13] = puVar4[3];
          *puVar4 = local_40;
          puVar4[1] = uStack_3c;
          puVar4[2] = uStack_38;
          puVar4[3] = uStack_34;
          if (puVar4[0x2b] != -0x40800000) {
            puVar4[0x2b] = DAT_00672fd0;
          }
        }
      }
      iVar2 = *(int *)(iVar2 + 4);
      if (iVar2 != 0) {
        puVar4 = local_30;
        puVar5 = (undefined4 *)(iVar2 + 0x10);
        for (iVar3 = 0xc; iVar3 != 0; iVar3 = iVar3 + -1) {
          *puVar5 = *puVar4;
          puVar4 = puVar4 + 1;
          puVar5 = puVar5 + 1;
        }
        *(undefined4 *)(iVar2 + 0xa0) = 1;
      }
      piVar1 = (int *)piVar1[1];
      local_44 = local_44 + 1;
      if (piVar1 == (int *)0x0) {
        iVar2 = 0;
      }
      else {
        iVar2 = *piVar1;
      }
    }
  }
  if (*(int *)((int)param_1 + 0x1e4) == 0) {
    CMonitor__Helper_004e1940(&DAT_00896988,*(void **)((int)param_1 + 0x59c),param_1);
  }
  *(undefined4 *)((int)param_1 + 0x1e4) = 1;
  return;
}
