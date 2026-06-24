/* address: 0x00477cb0 */
/* name: CSquadNormal__SelectBestEngagementTarget */
/* signature: int * __stdcall CSquadNormal__SelectBestEngagementTarget(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int * CSquadNormal__SelectBestEngagementTarget(void *param_1)

{
  undefined4 *puVar1;
  uint uVar2;
  float fVar3;
  bool bVar4;
  float fVar5;
  void *this;
  int iVar6;
  int iVar7;
  int *piVar8;
  int *piVar9;
  float10 fVar10;
  float10 extraout_ST0;
  float10 extraout_ST0_00;
  void *unaff_retaddr;
  float *pfVar11;
  float fVar12;
  float fStack_24;
  int *local_20;
  float fStack_14;
  float local_10;
  float fStack_c;
  undefined4 uStack_8;

  piVar8 = &DAT_00855090;
  if (*(int *)((int)param_1 + 0x7c) == 1) {
    piVar8 = &DAT_008550b0;
  }
  else if (*(int *)((int)param_1 + 0x7c) == 0) {
    piVar8 = &DAT_008550c0;
  }
  pfVar11 = &local_10;
  piVar9 = (int *)0x0;
  local_20 = (int *)0xbf800000;
  (**(code **)(*(int *)param_1 + 0x120))();
  this = (void *)(**(code **)(*(int *)param_1 + 0x124))();
  if (this != (void *)0x0) {
    puVar1 = (undefined4 *)*piVar8;
    if (puVar1 == (undefined4 *)0x0) {
      piVar8 = (int *)0x0;
    }
    else {
      piVar8 = (int *)*puVar1;
    }
    while (piVar8 != (int *)0x0) {
      if ((piVar8[0xd] & 0x20000000U) == 0) {
        if ((piVar8[0xd] & 0x10U) != 0) goto LAB_00477d6b;
      }
      else {
        piVar8 = (int *)(**(code **)(*piVar8 + 300))(fStack_14,local_10,fStack_c,uStack_8);
LAB_00477d6b:
        if (piVar8 != (int *)0x0) {
          iVar7 = *(int *)((int)param_1 + 0xa0);
          fVar3 = ((float)piVar8[7] - fStack_14) * ((float)piVar8[7] - fStack_14) +
                  ((float)piVar8[8] - local_10) * ((float)piVar8[8] - local_10) +
                  ((float)piVar8[9] - fStack_c) * ((float)piVar8[9] - fStack_c);
          bVar4 = true;
          fVar10 = (float10)(**(code **)(*piVar8 + 0x16c))();
          if ((fVar10 != (float10)_DAT_005d856c) &&
             (fVar10 = (float10)(**(code **)(*piVar8 + 0x16c))(),
             fVar10 = ((float10)_DAT_005d8568 - fVar10 * (float10)_DAT_005d85fc) *
                      (float10)*(float *)(iVar7 + 0x158), fVar10 * fVar10 < (float10)fVar3)) {
            bVar4 = false;
          }
          iVar6 = CSquadNormal__IsFactionCompatible(unaff_retaddr,piVar8[0x4e],(int)pfVar11);
          if (((iVar6 != 0) &&
              (iVar6 = CSquadNormal__IsValidLinkedSupportForTarget(this,(int)piVar8,pfVar11),
              iVar6 != 0)) && (bVar4)) {
            uVar2 = piVar8[0xd];
            if ((uVar2 & 0x20000) == 0) {
              if ((uVar2 & 0x4000) == 0) {
                if ((uVar2 & 0x400) == 0) {
                  if ((uVar2 & 0x80000) == 0) {
                    if ((uVar2 & 0x40000) == 0) {
                      if ((uVar2 & 0x100) == 0) {
                        fVar12 = _DAT_005d856c;
                        if ((uVar2 & 0x8000) != 0) {
                          fVar12 = *(float *)(iVar7 + 0x170);
                        }
                      }
                      else {
                        fVar12 = *(float *)(iVar7 + 0x16c);
                      }
                    }
                    else {
                      fVar12 = *(float *)(iVar7 + 0x164);
                    }
                  }
                  else {
                    fVar12 = *(float *)(iVar7 + 0x17c);
                  }
                }
                else {
                  fVar12 = *(float *)(iVar7 + 0x178);
                }
              }
              else {
                fVar12 = *(float *)(iVar7 + 0x174);
              }
            }
            else {
              fVar12 = *(float *)(iVar7 + 0x168);
            }
            fVar3 = SQRT(fVar3);
            fVar12 = fVar12 * _DAT_005d85cc + (_DAT_005d8c54 - fVar3);
            CSquadNormal__SelectBestSupportOrEscort(this,piVar8,(int)pfVar11);
            CSquadNormal__GetSupportMinEngageDistance();
            if (extraout_ST0 <= (float10)fVar3) {
              CSquadNormal__GetSupportMaxEngageDistance();
              fVar5 = _DAT_005dbc64;
              if (extraout_ST0_00 < (float10)fVar3) {
                fVar5 = _DAT_005db3b4;
              }
              fVar12 = fVar12 + fVar5;
            }
            iVar7 = (**(code **)(*piVar8 + 0x164))();
            if ((iVar7 == 0) && (iVar7 = (**(code **)(*piVar8 + 0x68))(), iVar7 == 0)) {
              fVar12 = _DAT_005d856c;
            }
            if ((*(int *)((int)unaff_retaddr + 0x9c) == 1) &&
               (fVar3 = (float)piVar8[7] - *(float *)((int)unaff_retaddr + 0x8c),
               fVar5 = (float)piVar8[8] - *(float *)((int)unaff_retaddr + 0x90),
               _DAT_005dbc60 < fVar3 * fVar3 + fVar5 * fVar5)) {
              fVar12 = _DAT_005d8be0;
            }
            if (fStack_24 < fVar12) {
              fStack_24 = fVar12;
              local_20 = piVar8;
            }
          }
        }
      }
      puVar1 = (undefined4 *)puVar1[1];
      piVar9 = local_20;
      param_1 = unaff_retaddr;
      if (puVar1 == (undefined4 *)0x0) {
        piVar8 = (int *)0x0;
      }
      else {
        piVar8 = (int *)*puVar1;
      }
    }
  }
  if ((piVar9 == (int *)0x0) || (piVar8 = (int *)piVar9[0x52], (int *)piVar9[0x52] == (int *)0x0)) {
    piVar8 = piVar9;
  }
  return piVar8;
}
