/* address: 0x004b6f70 */
/* name: CMessage__WordWrapToLineBuffer */
/* signature: void __thiscall CMessage__WordWrapToLineBuffer(void * this, int param_1, void * param_2, int param_3, int param_4) */


void __thiscall
CMessage__WordWrapToLineBuffer(void *this,int param_1,void *param_2,int param_3,int param_4)

{
  short sVar1;
  short *wstr;
  int iVar2;
  bool bVar3;
  int iVar4;
  int iVar5;
  short *psVar6;
  undefined1 *puVar7;
  int iVar8;
  undefined2 *puVar9;
  int iVar10;
  int iVar11;
  undefined2 *puVar12;
  int iVar13;
  int iVar14;
  int local_28;
  int local_24;
  short local_c;
  short local_a;
  short local_8;
  short local_6;

  wstr = *(short **)((int)this + 0xc);
  iVar2 = *(int *)((int)this + 0x1c);
  iVar5 = WcsLen(wstr);
  iVar13 = 0;
  iVar5 = iVar5 + *(int *)((int)this + 0x34);
  iVar14 = 0;
  local_24 = 0;
  psVar6 = Text__AsciiToWideScratch(&DAT_00629b00);
  CUnitAI__Helper_0055e64e(&local_c,psVar6);
  iVar10 = 8;
  puVar7 = (undefined1 *)param_1;
  do {
    *puVar7 = 0;
    puVar7[1] = 0;
    puVar7 = puVar7 + 0xac;
    iVar10 = iVar10 + -1;
  } while (iVar10 != 0);
  iVar10 = iVar2 + *(int *)((int)this + 0x34);
  if (0 < iVar10) {
    local_28 = 0;
    do {
      iVar8 = 0;
      if (iVar14 < iVar2) {
        bVar3 = false;
        psVar6 = wstr + iVar14;
        do {
          if (iVar5 <= iVar8 + iVar14) {
            bVar3 = true;
          }
          if (((*psVar6 == 0x20) &&
              ((iVar11 = iVar8 + 1 + iVar14, iVar5 <= iVar11 ||
               ((((sVar1 = wstr[iVar11], sVar1 != local_c && (sVar1 != local_a)) &&
                 (sVar1 != local_8)) && (sVar1 != local_6)))))) || (bVar3)) goto LAB_004b7071;
          iVar8 = iVar8 + 1;
          psVar6 = psVar6 + 1;
        } while ((*(int *)((int)this + 0x34) == 0) || (iVar8 + iVar14 < iVar2));
        iVar8 = iVar8 + *(int *)((int)this + 0x34);
      }
      else {
        iVar8 = (iVar2 - iVar14) + 5;
      }
LAB_004b7071:
      iVar11 = local_28;
      iVar4 = local_24;
      if ((int)param_2 <= iVar8 + iVar13) {
        iVar8 = local_28 + iVar13;
        iVar13 = 0;
        *(undefined2 *)(param_1 + iVar8 * 2) = 0;
        iVar11 = local_28 + 0x56;
        iVar4 = local_24 + 1;
        if (param_3 <= local_24 + 1) {
          iVar8 = 7;
          puVar12 = (undefined2 *)param_1;
          do {
            iVar11 = 0x55;
            puVar9 = puVar12;
            do {
              *puVar9 = puVar9[0x56];
              puVar9 = puVar9 + 1;
              iVar11 = iVar11 + -1;
            } while (iVar11 != 0);
            puVar12 = puVar12 + 0x56;
            iVar8 = iVar8 + -1;
            iVar11 = local_28;
            iVar4 = local_24;
          } while (iVar8 != 0);
        }
      }
      local_24 = iVar4;
      local_28 = iVar11;
      if ((wstr[iVar14] != 0x20) || (iVar13 != 0)) {
        if (iVar14 < iVar2) {
          iVar8 = local_28 + iVar13;
          iVar13 = iVar13 + 1;
          *(short *)(param_1 + iVar8 * 2) = wstr[iVar14];
        }
        else {
          iVar8 = local_28 + iVar13;
          iVar13 = iVar13 + 1;
          *(undefined2 *)(param_1 + iVar8 * 2) = 0x2e;
        }
      }
      iVar14 = iVar14 + 1;
    } while (iVar14 < iVar10);
  }
  *(undefined2 *)(param_1 + (iVar13 + local_24 * 0x56) * 2) = 0;
  return;
}
