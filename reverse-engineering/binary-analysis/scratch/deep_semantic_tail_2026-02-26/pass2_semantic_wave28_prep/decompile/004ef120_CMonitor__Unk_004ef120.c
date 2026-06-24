/* address: 0x004ef120 */
/* name: CMonitor__Unk_004ef120 */
/* signature: void __fastcall CMonitor__Unk_004ef120(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CMonitor__Unk_004ef120(int param_1)

{
  int iVar1;
  int *piVar2;
  float fVar3;
  bool bVar4;
  int iVar5;
  undefined4 *puVar6;
  int iVar7;
  int local_28;
  undefined1 local_10 [16];

  if (*(int *)(param_1 + 0x164) != 0) {
    iVar1 = *(int *)(*(int *)(param_1 + 0x164) + 0xec);
    iVar7 = 0;
    piVar2 = (int *)*DAT_008553f8;
    DAT_008553f8[2] = (int)piVar2;
    if (piVar2 == (int *)0x0) {
      iVar5 = 0;
    }
    else {
      iVar5 = *piVar2;
    }
    if (iVar5 != 0) {
      while (iVar7 != iVar1) {
        iVar7 = iVar7 + 1;
        piVar2 = *(int **)(DAT_008553f8[2] + 4);
        DAT_008553f8[2] = (int)piVar2;
        if (piVar2 == (int *)0x0) {
          iVar5 = 0;
        }
        else {
          iVar5 = *piVar2;
        }
        if (iVar5 == 0) {
          return;
        }
      }
      if ((iVar5 != 0) && (*(int *)(iVar5 + 4) != 0)) {
        bVar4 = false;
        local_28 = 0;
        do {
          if (99 < local_28) {
            return;
          }
          if (*(int **)(param_1 + 0x30) == (int *)0x0) {
            puVar6 = (undefined4 *)(param_1 + 0x1c);
          }
          else {
            puVar6 = (undefined4 *)(**(code **)(**(int **)(param_1 + 0x30) + 0x20))(local_10,0);
          }
          fVar3 = (float)puVar6[2];
          if ((DAT_006fbdfc < fVar3) && (fVar3 < DAT_006fbdfc + _DAT_005d8568)) {
            CParticleManager__CreateEffect
                      (*(undefined4 *)(iVar5 + 4),0,*puVar6,puVar6[1],fVar3,puVar6[3],0,0);
            bVar4 = true;
          }
          local_28 = local_28 + 1;
        } while (!bVar4);
      }
    }
  }
  return;
}
