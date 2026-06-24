/* address: 0x005475d0 */
/* name: CDXEngine__Unk_005475d0 */
/* signature: void __stdcall CDXEngine__Unk_005475d0(float param_1, float param_2, int param_3) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void CDXEngine__Unk_005475d0(float param_1,float param_2,int param_3)

{
  int *piVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  byte *pbVar5;
  int iVar6;
  int iVar7;
  uint uVar8;
  int iVar9;
  float fVar10;
  int *piVar11;
  float fVar12;
  int iVar13;
  uint uVar14;
  int iVar15;
  uint uVar16;
  uint uVar17;
  uint unaff_EDI;
  int iVar18;
  double dVar19;
  longlong lVar20;
  int local_30;
  float local_28;
  int local_1c;
  int local_8;

  if (_DAT_005d8c60 <=
      (param_1 - _DAT_00650ab0) * (param_1 - _DAT_00650ab0) +
      (param_2 - _DAT_00650ab4) * (param_2 - _DAT_00650ab4)) {
    _DAT_00650ab4 = param_2;
    _DAT_00650ab0 = param_1;
    iVar9 = param_3;
    if (param_3 < 0) {
      iVar9 = -param_3;
    }
    iVar9 = 1 << ((byte)iVar9 & 0x1f);
    dVar19 = CDXEngine__Helper_0055dfe7((double)(param_1 * _DAT_005d8bc0));
    local_8 = (int)(longlong)ROUND(dVar19);
    uVar16 = local_8 - (iVar9 >> 1);
    dVar19 = CDXEngine__Helper_0055dfe7((double)(param_2 * _DAT_005d8bc0));
    local_8 = (int)(longlong)ROUND(dVar19);
    uVar8 = local_8 - (iVar9 >> 1);
    fVar10 = (float)((int)uVar16 >> 7);
    iVar15 = (int)uVar8 >> 7;
    if ((((-1 < (int)fVar10) && (-1 < iVar15)) && ((int)fVar10 < 0x40)) && (iVar15 < 0x40)) {
      uVar16 = uVar16 & 0x7f;
      uVar8 = uVar8 & 0x7f;
      lVar20 = (ulonglong)unaff_EDI << 0x20;
      fVar12 = 1.4013e-45;
      param_2 = 1.4013e-45;
      if ((0x80 < (int)(uVar16 + iVar9)) && ((int)fVar10 < 0x3f)) {
        param_2 = 2.8026e-45;
        fVar12 = 2.8026e-45;
      }
      local_1c = 1;
      if ((0x80 < (int)(iVar9 + uVar8)) && (iVar15 < 0x3f)) {
        local_1c = 2;
      }
      do {
        if (fVar12 != 0.0) {
          uVar14 = uVar16;
          param_1 = fVar10;
          local_28 = fVar12;
          do {
            uVar2 = (int)param_1 + iVar15 * 0x40;
            iVar9 = (int)((ulonglong)lVar20 >> 0x20);
            if (param_3 < 1) {
              lVar20 = CONCAT44(iVar9,uVar8);
              CDamage__Unk_00440f80(&DAT_008aa9f0,uVar2,uVar14,uVar8,iVar9);
            }
            else {
              lVar20 = CONCAT44(iVar9,param_3);
              CDamage__Unk_00440eb0();
            }
            if (*(int *)(DAT_0089c9b0 + 0x30) != 0) {
              piVar1 = (int *)(DAT_0089c9b0 + 0x20);
              if ((*(int *)(DAT_0089c9b0 + 0x20) != 0) &&
                 (local_30 = 0, 0 < *(int *)(DAT_0089c9b0 + 0x20))) {
                piVar11 = (int *)(DAT_0089c9b0 + 0x24);
                iVar9 = 0;
                do {
                  iVar13 = 1;
                  iVar6 = *piVar11;
                  if (1 < *(int *)(iVar6 + 0xc + iVar9)) {
                    iVar18 = 0x50;
                    uVar17 = uVar2 & 0xffff;
                    do {
                      iVar7 = *(int *)(iVar6 + iVar9);
                      iVar6 = iVar18 + -6;
                      iVar3 = iVar18 + -0x1c;
                      iVar4 = iVar18 + -0x50 + iVar7;
                      iVar18 = iVar18 + 0x50;
                      pbVar5 = (byte *)(*(int *)(iVar4 + 0x40) + 1 +
                                       (((*(ushort *)(iVar6 + iVar7) & uVar17) >>
                                        (*(byte *)(iVar3 + iVar7) & 0x1f)) +
                                       (*(ushort *)(iVar4 + 0x48) & uVar17)) * 2);
                      *pbVar5 = *pbVar5 | 0x80;
                      iVar13 = iVar13 + 1;
                      iVar6 = *piVar11;
                    } while (iVar13 < *(int *)(iVar6 + 0xc + iVar9));
                  }
                  local_30 = local_30 + 1;
                  iVar9 = iVar9 + 0x34;
                } while (local_30 < *piVar1);
              }
            }
            uVar14 = uVar14 - 0x80;
            param_1 = (float)((int)param_1 + 1);
            local_28 = (float)((int)local_28 + -1);
            fVar12 = param_2;
          } while (local_28 != 0.0);
        }
        iVar15 = iVar15 + 1;
        uVar8 = uVar8 - 0x80;
        local_1c = local_1c + -1;
      } while (local_1c != 0);
    }
  }
  return;
}
