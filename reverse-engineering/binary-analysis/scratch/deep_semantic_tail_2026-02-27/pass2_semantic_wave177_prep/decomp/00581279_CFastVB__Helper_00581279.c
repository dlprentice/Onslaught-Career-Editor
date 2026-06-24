/* address: 0x00581279 */
/* name: CFastVB__Helper_00581279 */
/* signature: int __thiscall CFastVB__Helper_00581279(void * this, int param_1, int param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __thiscall CFastVB__Helper_00581279(void *this,int param_1,int param_2)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  undefined4 *puVar5;
  float *pfVar6;
  int iVar7;
  uint uVar8;

  fVar4 = _DAT_005e9324;
  fVar1 = _DAT_005e72d4;
  fVar2 = _DAT_005e6a38;
  fVar3 = _DAT_005e6a34;
  iVar7 = *(int *)((int)this + 8);
  if (iVar7 == 1) {
    iVar7 = *(int *)((int)this + 0x1050);
    if (iVar7 == 2) {
      uVar8 = 0;
      if (*(int *)((int)this + 0x1060) != 0) {
        pfVar6 = (float *)(param_1 + 8);
        iVar7 = 0;
        do {
          uVar8 = uVar8 + 1;
          *(float *)(iVar7 + *(int *)((int)this + 0x1054)) = (pfVar6[-2] + fVar3) * fVar1;
          *(float *)(iVar7 + 4 + *(int *)((int)this + 0x1054)) = (pfVar6[-1] + fVar3) * fVar1;
          *(float *)(iVar7 + 8 + *(int *)((int)this + 0x1054)) = (*pfVar6 + fVar3) * fVar1;
          *(float *)(iVar7 + 0xc + *(int *)((int)this + 0x1054)) = pfVar6[1];
          pfVar6 = pfVar6 + 4;
          iVar7 = iVar7 + 0x10;
        } while (uVar8 < *(uint *)((int)this + 0x1060));
      }
    }
    else if (iVar7 == 3) {
      uVar8 = 0;
      if (*(int *)((int)this + 0x1060) != 0) {
        iVar7 = 0;
        pfVar6 = (float *)(param_1 + 8);
        do {
          uVar8 = uVar8 + 1;
          *(float *)(iVar7 + *(int *)((int)this + 0x1054)) = (pfVar6[-2] + fVar3) * fVar1;
          iVar7 = iVar7 + 0x10;
          *(float *)(*(int *)((int)this + 0x1054) + -0xc + iVar7) = (pfVar6[-1] + fVar3) * fVar1;
          *(float *)(*(int *)((int)this + 0x1054) + -8 + iVar7) = (*pfVar6 + fVar3) * fVar1;
          *(float *)(*(int *)((int)this + 0x1054) + -4 + iVar7) = (pfVar6[1] + fVar3) * fVar1;
          pfVar6 = pfVar6 + 4;
        } while (uVar8 < *(uint *)((int)this + 0x1060));
      }
    }
    else if ((iVar7 == 4) && (uVar8 = 0, *(int *)((int)this + 0x1060) != 0)) {
      pfVar6 = (float *)(param_1 + 8);
      iVar7 = -8 - param_1;
      do {
        if (0.0 <= pfVar6[-2]) {
          if (fVar3 <= pfVar6[-2]) {
            fVar2 = 1.0;
          }
          else {
            fVar2 = pfVar6[-2];
          }
        }
        else {
          fVar2 = 0.0;
        }
        *(float *)((int)pfVar6 + *(int *)((int)this + 0x1054) + iVar7) = fVar2;
        if (0.0 <= pfVar6[-1]) {
          if (fVar3 <= pfVar6[-1]) {
            fVar2 = 1.0;
          }
          else {
            fVar2 = pfVar6[-1];
          }
        }
        else {
          fVar2 = 0.0;
        }
        *(float *)((int)pfVar6 + *(int *)((int)this + 0x1054) + 4 + iVar7) = fVar2;
        if (0.0 <= *pfVar6) {
          if (fVar3 <= *pfVar6) {
            fVar2 = 1.0;
          }
          else {
            fVar2 = *pfVar6;
          }
        }
        else {
          fVar2 = 0.0;
        }
        *(float *)((int)pfVar6 + *(int *)((int)this + 0x1054) + 8 + iVar7) = fVar2;
        if (0.0 <= pfVar6[1]) {
          if (fVar3 <= pfVar6[1]) {
            fVar2 = 1.0;
          }
          else {
            fVar2 = pfVar6[1];
          }
        }
        else {
          fVar2 = 0.0;
        }
        uVar8 = uVar8 + 1;
        *(float *)((int)pfVar6 + *(int *)((int)this + 0x1054) + 0xc + iVar7) = fVar2;
        pfVar6 = pfVar6 + 4;
      } while (uVar8 < *(uint *)((int)this + 0x1060));
    }
  }
  else if (iVar7 == 2) {
    iVar7 = *(int *)((int)this + 0x1050);
    if (iVar7 == 1) {
      uVar8 = 0;
      if (*(int *)((int)this + 0x1060) != 0) {
        pfVar6 = (float *)(param_1 + 8);
        iVar7 = 0;
        do {
          uVar8 = uVar8 + 1;
          *(float *)(iVar7 + *(int *)((int)this + 0x1054)) = pfVar6[-2] * fVar4 - fVar3;
          *(float *)(iVar7 + 4 + *(int *)((int)this + 0x1054)) = pfVar6[-1] * fVar4 - fVar3;
          *(float *)(iVar7 + 8 + *(int *)((int)this + 0x1054)) = *pfVar6 * fVar4 - fVar3;
          *(float *)(iVar7 + 0xc + *(int *)((int)this + 0x1054)) = pfVar6[1];
          pfVar6 = pfVar6 + 4;
          iVar7 = iVar7 + 0x10;
        } while (uVar8 < *(uint *)((int)this + 0x1060));
      }
    }
    else if (iVar7 == 3) {
      uVar8 = 0;
      if (*(int *)((int)this + 0x1060) != 0) {
        puVar5 = (undefined4 *)(param_1 + 8);
        iVar7 = 0;
        do {
          *(undefined4 *)(iVar7 + *(int *)((int)this + 0x1054)) = puVar5[-2];
          uVar8 = uVar8 + 1;
          *(undefined4 *)(iVar7 + 4 + *(int *)((int)this + 0x1054)) = puVar5[-1];
          *(undefined4 *)(iVar7 + 8 + *(int *)((int)this + 0x1054)) = *puVar5;
          pfVar6 = (float *)(puVar5 + 1);
          puVar5 = puVar5 + 4;
          *(float *)(iVar7 + 0xc + *(int *)((int)this + 0x1054)) =
               (*pfVar6 + _DAT_005e6a34) * _DAT_005e72d4;
          iVar7 = iVar7 + 0x10;
        } while (uVar8 < *(uint *)((int)this + 0x1060));
      }
    }
    else if ((iVar7 == 4) && (uVar8 = 0, *(int *)((int)this + 0x1060) != 0)) {
      pfVar6 = (float *)(param_1 + 8);
      iVar7 = -param_1;
      do {
        fVar1 = fVar2;
        if (fVar2 <= pfVar6[-2]) {
          if (fVar3 <= pfVar6[-2]) {
            fVar1 = 1.0;
          }
          else {
            fVar1 = pfVar6[-2];
          }
        }
        *(float *)((int)pfVar6 + *(int *)((int)this + 0x1054) + iVar7 + -8) = fVar1;
        fVar1 = fVar2;
        if (fVar2 <= pfVar6[-1]) {
          if (fVar3 <= pfVar6[-1]) {
            fVar1 = 1.0;
          }
          else {
            fVar1 = pfVar6[-1];
          }
        }
        *(float *)((int)pfVar6 + *(int *)((int)this + 0x1054) + iVar7 + -4) = fVar1;
        fVar1 = fVar2;
        if (fVar2 <= *pfVar6) {
          if (fVar3 <= *pfVar6) {
            fVar1 = 1.0;
          }
          else {
            fVar1 = *pfVar6;
          }
        }
        *(float *)((int)pfVar6 + *(int *)((int)this + 0x1054) + iVar7) = fVar1;
        if (0.0 <= pfVar6[1]) {
          if (fVar3 <= pfVar6[1]) {
            fVar1 = 1.0;
          }
          else {
            fVar1 = pfVar6[1];
          }
        }
        else {
          fVar1 = 0.0;
        }
        uVar8 = uVar8 + 1;
        *(float *)((int)pfVar6 + *(int *)((int)this + 0x1054) + iVar7 + 4) = fVar1;
        pfVar6 = pfVar6 + 4;
      } while (uVar8 < *(uint *)((int)this + 0x1060));
    }
  }
  else if (iVar7 == 3) {
    iVar7 = *(int *)((int)this + 0x1050);
    if (iVar7 == 1) {
      uVar8 = 0;
      if (*(int *)((int)this + 0x1060) != 0) {
        pfVar6 = (float *)(param_1 + 8);
        iVar7 = 0;
        do {
          uVar8 = uVar8 + 1;
          *(float *)(iVar7 + *(int *)((int)this + 0x1054)) = pfVar6[-2] * fVar4 - fVar3;
          *(float *)(iVar7 + 4 + *(int *)((int)this + 0x1054)) = pfVar6[-1] * fVar4 - fVar3;
          *(float *)(iVar7 + 8 + *(int *)((int)this + 0x1054)) = *pfVar6 * fVar4 - fVar3;
          *(float *)(iVar7 + 0xc + *(int *)((int)this + 0x1054)) = pfVar6[1] * fVar4 - fVar3;
          pfVar6 = pfVar6 + 4;
          iVar7 = iVar7 + 0x10;
        } while (uVar8 < *(uint *)((int)this + 0x1060));
      }
    }
    else if (iVar7 == 2) {
      uVar8 = 0;
      if (*(int *)((int)this + 0x1060) != 0) {
        iVar7 = 0;
        puVar5 = (undefined4 *)(param_1 + 8);
        do {
          *(undefined4 *)(iVar7 + *(int *)((int)this + 0x1054)) = puVar5[-2];
          uVar8 = uVar8 + 1;
          *(undefined4 *)(*(int *)((int)this + 0x1054) + 4 + iVar7) = puVar5[-1];
          iVar7 = iVar7 + 0x10;
          *(undefined4 *)(*(int *)((int)this + 0x1054) + -8 + iVar7) = *puVar5;
          pfVar6 = (float *)(puVar5 + 1);
          puVar5 = puVar5 + 4;
          *(float *)(*(int *)((int)this + 0x1054) + -4 + iVar7) =
               (*pfVar6 + *pfVar6) - _DAT_005e6a34;
        } while (uVar8 < *(uint *)((int)this + 0x1060));
      }
    }
    else if ((iVar7 == 4) && (uVar8 = 0, *(int *)((int)this + 0x1060) != 0)) {
      pfVar6 = (float *)(param_1 + 8);
      iVar7 = -8 - param_1;
      do {
        fVar1 = fVar2;
        if (fVar2 <= pfVar6[-2]) {
          if (fVar3 <= pfVar6[-2]) {
            fVar1 = 1.0;
          }
          else {
            fVar1 = pfVar6[-2];
          }
        }
        *(float *)((int)pfVar6 + *(int *)((int)this + 0x1054) + iVar7) = fVar1;
        fVar1 = fVar2;
        if (fVar2 <= pfVar6[-1]) {
          if (fVar3 <= pfVar6[-1]) {
            fVar1 = 1.0;
          }
          else {
            fVar1 = pfVar6[-1];
          }
        }
        *(float *)((int)pfVar6 + *(int *)((int)this + 0x1054) + 4 + iVar7) = fVar1;
        fVar1 = fVar2;
        if (fVar2 <= *pfVar6) {
          if (fVar3 <= *pfVar6) {
            fVar1 = 1.0;
          }
          else {
            fVar1 = *pfVar6;
          }
        }
        *(float *)((int)pfVar6 + *(int *)((int)this + 0x1054) + 8 + iVar7) = fVar1;
        fVar1 = fVar2;
        if (fVar2 <= pfVar6[1]) {
          if (fVar3 <= pfVar6[1]) {
            fVar1 = 1.0;
          }
          else {
            fVar1 = pfVar6[1];
          }
        }
        uVar8 = uVar8 + 1;
        *(float *)((int)pfVar6 + *(int *)((int)this + 0x1054) + 0xc + iVar7) = fVar1;
        pfVar6 = pfVar6 + 4;
      } while (uVar8 < *(uint *)((int)this + 0x1060));
    }
  }
  return *(int *)((int)this + 0x1054);
}
