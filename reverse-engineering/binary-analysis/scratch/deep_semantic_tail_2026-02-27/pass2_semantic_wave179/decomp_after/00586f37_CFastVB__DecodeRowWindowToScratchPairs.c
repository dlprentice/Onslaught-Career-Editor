/* address: 0x00586f37 */
/* name: CFastVB__DecodeRowWindowToScratchPairs */
/* signature: int __thiscall CFastVB__DecodeRowWindowToScratchPairs(void * this, int param_1, uint param_2, uint param_3, uint param_4) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __thiscall
CFastVB__DecodeRowWindowToScratchPairs
          (void *this,int param_1,uint param_2,uint param_3,uint param_4)

{
  undefined2 uVar1;
  ushort uVar2;
  ushort uVar3;
  undefined2 uVar4;
  float fVar5;
  float fVar6;
  float fVar7;
  float fVar8;
  float fVar9;
  float fVar10;
  float fVar11;
  float fVar12;
  float fVar13;
  float fVar14;
  int iVar15;
  int iVar16;
  float *pfVar17;
  ushort *puVar18;

  if (*(int *)((int)this + 0x1098) == 0) {
    return -0x7ff8fff2;
  }
  if (((((uint)param_1 < *(uint *)((int)this + 0x107c)) ||
       (*(uint *)((int)this + 0x1084) <= (uint)param_1)) ||
      (param_2 < *(uint *)((int)this + 0x1088))) || (*(uint *)((int)this + 0x108c) <= param_2)) {
    iVar15 = CFastVB__FlushPendingConvertedRows16((int)this);
    if (iVar15 < 0) {
      return iVar15;
    }
    *(int *)((int)this + 0x1084) = param_1 + 1;
    *(int *)((int)this + 0x107c) = param_1;
    *(uint *)((int)this + 0x1088) = param_2;
    *(uint *)((int)this + 0x108c) = param_2 + 1;
    fVar14 = _DAT_005ea1f0;
    fVar5 = _DAT_005e9ee0;
    fVar13 = DAT_005e6a3c;
    fVar12 = _DAT_005e6a34;
    if (param_3 != 0) {
      iVar16 = *(int *)((int)this + 0x1058) * param_1;
      param_1 = *(uint *)((int)this + 0x1078);
      pfVar17 = *(float **)((int)this + 0x1074);
      iVar15 = *(int *)((int)this + 4);
      puVar18 = (ushort *)
                (iVar16 + *(int *)((int)this + 0x105c) * param_2 + param_1 * 2 +
                *(int *)((int)this + 0x20));
      if (iVar15 != 0x32595559) {
        if ((iVar15 == 0x42475247) || (iVar15 == 0x47424752)) {
          if (*(uint *)((int)this + 0x1080) <= (uint)param_1) {
            return 0;
          }
          do {
            uVar1 = *(undefined2 *)((int)this + 0x109c);
            uVar2 = *puVar18;
            param_1 = param_1 + 2;
            uVar3 = puVar18[1];
            fVar12 = (float)(uVar2 >> ((byte)*(undefined2 *)((int)this + 0x10a0) & 0x1f) & 0xff) *
                     fVar5;
            uVar4 = *(undefined2 *)((int)this + 0x10a0);
            pfVar17[5] = (float)(uVar3 >> ((byte)*(undefined2 *)((int)this + 0x109c) & 0x1f) & 0xff)
                         * fVar5;
            fVar13 = (float)(uVar3 >> ((byte)uVar4 & 0x1f) & 0xff) * fVar5;
            *pfVar17 = fVar12;
            pfVar17[1] = (float)(uVar2 >> ((byte)uVar1 & 0x1f) & 0xff) * fVar5;
            pfVar17[2] = fVar13;
            pfVar17[3] = 1.0;
            pfVar17[4] = fVar12;
            pfVar17[6] = fVar13;
            pfVar17[7] = 1.0;
            pfVar17 = pfVar17 + 8;
            puVar18 = puVar18 + 2;
          } while ((uint)param_1 < *(uint *)((int)this + 0x1080));
          return 0;
        }
        if (iVar15 != 0x59565955) {
          return 0;
        }
      }
      param_3 = param_1;
      if ((uint)param_1 < *(uint *)((int)this + 0x1080)) {
        do {
          uVar1 = *(undefined2 *)((int)this + 0x109c);
          uVar2 = puVar18[1];
          fVar10 = (float)(*puVar18 >> ((byte)*(undefined2 *)((int)this + 0x10a0) & 0x1f) & 0xff) -
                   _DAT_005ea1ec;
          fVar7 = (float)(uVar2 >> ((byte)*(undefined2 *)((int)this + 0x10a0) & 0x1f) & 0xff) -
                  _DAT_005ea1ec;
          fVar8 = fVar7 * _DAT_005ea1e8;
          fVar6 = ((float)(*puVar18 >> ((byte)*(undefined2 *)((int)this + 0x109c) & 0x1f) & 0xff) -
                  fVar14) * _DAT_005ea1e4;
          fVar9 = fVar6 + fVar8;
          *pfVar17 = fVar9;
          fVar11 = fVar10 * _DAT_005ea1e0;
          fVar7 = fVar7 * _DAT_005ea1dc;
          fVar5 = (fVar6 - fVar11) - fVar7;
          pfVar17[1] = fVar5;
          fVar10 = fVar10 * _DAT_005ea1d8;
          fVar6 = fVar10 + fVar6;
          pfVar17[2] = fVar6;
          pfVar17[3] = 1.0;
          if (fVar13 <= fVar9) {
            if (fVar12 < fVar9) {
              fVar9 = 1.0;
            }
          }
          else {
            fVar9 = 0.0;
          }
          *pfVar17 = fVar9;
          if (fVar13 <= fVar5) {
            if (fVar12 < fVar5) {
              fVar5 = 1.0;
            }
          }
          else {
            fVar5 = 0.0;
          }
          pfVar17[1] = fVar5;
          if (fVar13 <= fVar6) {
            if (fVar12 < fVar6) {
              fVar6 = 1.0;
            }
          }
          else {
            fVar6 = 0.0;
          }
          pfVar17[2] = fVar6;
          fVar5 = ((float)(uVar2 >> ((byte)uVar1 & 0x1f) & 0xff) - fVar14) * _DAT_005ea1e4;
          fVar8 = fVar5 + fVar8;
          pfVar17[4] = fVar8;
          fVar7 = (fVar5 - fVar11) - fVar7;
          pfVar17[5] = fVar7;
          fVar5 = fVar5 + fVar10;
          pfVar17[6] = fVar5;
          pfVar17[7] = 1.0;
          if (fVar13 <= fVar8) {
            if (fVar12 < fVar8) {
              fVar8 = 1.0;
            }
          }
          else {
            fVar8 = 0.0;
          }
          pfVar17[4] = fVar8;
          if (fVar13 <= fVar7) {
            if (fVar12 < fVar7) {
              fVar7 = 1.0;
            }
          }
          else {
            fVar7 = 0.0;
          }
          pfVar17[5] = fVar7;
          if (fVar13 <= fVar5) {
            if (fVar12 < fVar5) {
              fVar5 = 1.0;
            }
          }
          else {
            fVar5 = 0.0;
          }
          param_3 = param_3 + 2;
          pfVar17[6] = fVar5;
          pfVar17 = pfVar17 + 8;
          puVar18 = puVar18 + 2;
        } while (param_3 < *(uint *)((int)this + 0x1080));
      }
    }
  }
  return 0;
}
