/* address: 0x005afbd0 */
/* name: CDXTexture__InterleaveComponentRowsIntoScanline */
/* signature: void __stdcall CDXTexture__InterleaveComponentRowsIntoScanline(int param_1, int param_2, int param_3, void * param_4, int param_5) */


void CDXTexture__InterleaveComponentRowsIntoScanline
               (int param_1,int param_2,int param_3,void *param_4,int param_5)

{
  int iVar1;
  int iVar2;
  int iVar3;
  undefined1 *puVar4;
  undefined1 *puVar5;
  int iVar6;
  int iVar7;
  int iVar8;

  iVar1 = *(int *)(param_1 + 0x24);
  iVar2 = *(int *)(param_1 + 0x70);
  if (-1 < param_5 + -1) {
    iVar6 = param_3 << 2;
    param_1 = param_5;
    do {
      iVar7 = 0;
      if (0 < iVar1) {
        iVar3 = *(int *)param_4;
        do {
          puVar4 = *(undefined1 **)(iVar6 + *(int *)(param_2 + iVar7 * 4));
          puVar5 = (undefined1 *)(iVar3 + iVar7);
          for (iVar8 = iVar2; iVar8 != 0; iVar8 = iVar8 + -1) {
            *puVar5 = *puVar4;
            puVar4 = puVar4 + 1;
            puVar5 = puVar5 + iVar1;
          }
          iVar7 = iVar7 + 1;
        } while (iVar7 < iVar1);
      }
      param_4 = (void *)((int)param_4 + 4);
      iVar6 = iVar6 + 4;
      param_1 = param_1 + -1;
    } while (param_1 != 0);
  }
  return;
}
