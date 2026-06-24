/* address: 0x00465a20 */
/* name: CFEPLanguageTest__Helper_00465a20 */
/* signature: int __stdcall CFEPLanguageTest__Helper_00465a20(void * param_1, void * param_2, float param_3) */


int CFEPLanguageTest__Helper_00465a20(void *param_1,void *param_2,float param_3)

{
  short sVar1;
  void *pvVar2;
  int iVar3;
  undefined2 *puVar4;
  short *psVar5;
  short *psVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  int local_1bc;
  void *local_1b8;
  int local_1b4;
  short local_1a8;
  short local_1a6;
  short local_1a4;
  short local_1a2;
  void *local_19c;
  int local_198 [2];
  short local_190 [200];

  iVar3 = WcsLen(param_2);
  iVar10 = 0;
  local_1b4 = 0;
  local_1bc = 0;
  iVar7 = 0x28;
  puVar4 = param_1;
  do {
    *puVar4 = 0;
    puVar4 = puVar4 + 100;
    iVar7 = iVar7 + -1;
  } while (iVar7 != 0);
  psVar5 = Text__AsciiToWideScratch(&DAT_00629b00);
  CRT__WStrCpy(&local_1a8,psVar5);
  iVar7 = 0;
  if (0 < iVar3) {
    local_1b8 = param_1;
    iVar8 = 0;
    do {
      psVar5 = (short *)((int)param_2 + local_1b4 * 2);
      psVar6 = psVar5;
      for (iVar7 = 0;
          ((iVar7 + local_1b4 != iVar3 &&
           (((((*psVar6 != 0x20 || (iVar9 = iVar7 + 1 + local_1b4, iVar3 <= iVar9)) ||
              (sVar1 = *(short *)((int)param_2 + iVar9 * 2), sVar1 == local_1a8)) ||
             ((sVar1 == local_1a6 || (sVar1 == local_1a4)))) || (sVar1 == local_1a2)))) &&
          (iVar7 < 99)); iVar7 = iVar7 + 1) {
        psVar6 = psVar6 + 1;
      }
      CRT__WcsNcpyZeroPad(local_190,local_1b8,iVar10);
      CRT__WcsNcpyZeroPad(local_190 + iVar10,psVar5,iVar7);
      local_190[iVar7 + iVar10] = 0;
      CDXFont__GetTextExtent(local_19c,local_190,local_198);
      iVar9 = iVar8;
      iVar7 = local_1bc;
      pvVar2 = local_1b8;
      if (param_3 <= (float)local_198[0]) {
        if (iVar10 != 0) {
          psVar6 = (short *)((int)param_1 + (iVar8 + iVar10) * 2 + -2);
          do {
            if (*psVar6 != 0x20) break;
            iVar10 = iVar10 + -1;
            psVar6 = psVar6 + -1;
          } while (iVar10 != 0);
        }
        iVar7 = iVar8 + iVar10;
        iVar10 = 0;
        *(undefined2 *)((int)param_1 + iVar7 * 2) = 0;
        iVar9 = iVar8 + 100;
        iVar7 = local_1bc + 1;
        pvVar2 = (void *)((int)local_1b8 + 200);
        if (3999 < iVar8 + 100) {
          iVar9 = iVar8;
          iVar7 = local_1bc;
          pvVar2 = local_1b8;
        }
      }
      local_1b8 = pvVar2;
      local_1bc = iVar7;
      if ((*psVar5 != 0x20) || (iVar10 != 0)) {
        iVar7 = iVar9 + iVar10;
        iVar10 = iVar10 + 1;
        *(short *)((int)param_1 + iVar7 * 2) = *psVar5;
      }
      local_1b4 = local_1b4 + 1;
      iVar7 = local_1bc;
      iVar8 = iVar9;
    } while (local_1b4 < iVar3);
  }
  *(undefined2 *)((int)param_1 + (iVar10 + iVar7 * 100) * 2) = 0;
  return iVar7 + 1;
}
