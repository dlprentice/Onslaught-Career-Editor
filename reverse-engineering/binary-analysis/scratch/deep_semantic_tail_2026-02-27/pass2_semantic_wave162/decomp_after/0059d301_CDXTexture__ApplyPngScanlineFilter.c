/* address: 0x0059d301 */
/* name: CDXTexture__ApplyPngScanlineFilter */
/* signature: void __stdcall CDXTexture__ApplyPngScanlineFilter(int param_1, int param_2, void * param_3, void * param_4, int param_5) */


void CDXTexture__ApplyPngScanlineFilter
               (int param_1,int param_2,void *param_3,void *param_4,int param_5)

{
  byte bVar1;
  byte bVar2;
  int iVar3;
  uint uVar4;
  byte bVar5;
  int iVar6;
  uint uVar7;
  char *pcVar8;
  int iVar9;
  char *pcVar10;
  int iVar11;
  byte *pbVar12;

  if (param_5 != 0) {
    if (param_5 == 1) {
      uVar4 = (int)(*(byte *)(param_2 + 0xb) + 7) >> 3;
      pcVar8 = (char *)(uVar4 + (int)param_3);
      if (uVar4 < *(uint *)(param_2 + 4)) {
        pcVar10 = pcVar8 + -uVar4;
        iVar6 = *(uint *)(param_2 + 4) - uVar4;
        do {
          *pcVar8 = *pcVar8 + *pcVar10;
          pcVar8 = pcVar8 + 1;
          pcVar10 = pcVar10 + 1;
          iVar6 = iVar6 + -1;
        } while (iVar6 != 0);
      }
    }
    else if (param_5 == 2) {
      uVar4 = *(uint *)(param_2 + 4);
      uVar7 = 0;
      if (uVar4 != 0) {
        do {
          *(char *)param_3 = *(char *)param_3 + *(char *)(uVar7 + (int)param_4);
          param_3 = (void *)((int)param_3 + 1);
          uVar7 = uVar7 + 1;
        } while (uVar7 < uVar4);
      }
    }
    else if (param_5 == 3) {
      iVar6 = (int)(*(byte *)(param_2 + 0xb) + 7) >> 3;
      iVar3 = *(int *)(param_2 + 4) - iVar6;
      pcVar8 = param_3;
      for (; iVar6 != 0; iVar6 = iVar6 + -1) {
        *pcVar8 = *pcVar8 + (*(byte *)param_4 >> 1);
        param_4 = (void *)((int)param_4 + 1);
        pcVar8 = pcVar8 + 1;
      }
      for (; iVar3 != 0; iVar3 = iVar3 + -1) {
        *pcVar8 = *pcVar8 + (char)(((uint)*(byte *)param_3 + (uint)*(byte *)param_4) / 2);
        param_3 = (void *)((int)param_3 + 1);
        param_4 = (void *)((int)param_4 + 1);
        pcVar8 = pcVar8 + 1;
      }
    }
    else if (param_5 == 4) {
      iVar3 = (int)(*(byte *)(param_2 + 0xb) + 7) >> 3;
      iVar6 = *(int *)(param_2 + 4) - iVar3;
      pcVar8 = param_3;
      pbVar12 = param_4;
      for (; iVar3 != 0; iVar3 = iVar3 + -1) {
        *pcVar8 = *pcVar8 + *pbVar12;
        pbVar12 = pbVar12 + 1;
        pcVar8 = pcVar8 + 1;
      }
      for (; iVar6 != 0; iVar6 = iVar6 + -1) {
        bVar5 = *(byte *)param_3;
        bVar1 = *pbVar12;
        bVar2 = *(byte *)param_4;
        param_3 = (void *)((int)param_3 + 1);
        pbVar12 = pbVar12 + 1;
        param_4 = (void *)((int)param_4 + 1);
        iVar3 = (uint)bVar1 - (uint)bVar2;
        iVar9 = (uint)bVar5 - (uint)bVar2;
        param_2 = iVar3;
        if (iVar3 < 0) {
          param_2 = -iVar3;
        }
        iVar11 = iVar9;
        if (iVar9 < 0) {
          iVar11 = -iVar9;
        }
        iVar3 = iVar3 + iVar9;
        if (iVar3 < 0) {
          iVar3 = -iVar3;
        }
        if (((iVar11 < param_2) || (iVar3 < param_2)) && (bVar5 = bVar1, iVar3 < iVar11)) {
          bVar5 = bVar2;
        }
        *pcVar8 = *pcVar8 + bVar5;
        pcVar8 = pcVar8 + 1;
      }
    }
    else {
      CDXTexture__Helper_00592d63(param_1,0x5f3a48);
      *(undefined1 *)param_3 = 0;
    }
  }
  return;
}
