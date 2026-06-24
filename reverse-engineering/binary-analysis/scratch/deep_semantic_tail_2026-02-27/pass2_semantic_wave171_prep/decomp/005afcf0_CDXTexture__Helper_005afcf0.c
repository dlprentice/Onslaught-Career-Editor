/* address: 0x005afcf0 */
/* name: CDXTexture__Helper_005afcf0 */
/* signature: void __stdcall CDXTexture__Helper_005afcf0(int param_1, void * param_2, int param_3, void * param_4, int param_5) */


void CDXTexture__Helper_005afcf0(int param_1,void *param_2,int param_3,void *param_4,int param_5)

{
  int *piVar1;
  int *piVar2;
  int *piVar3;
  byte bVar4;
  byte bVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  int iVar11;
  int iVar12;
  int iVar13;
  int iVar14;
  int iVar15;
  byte *pbVar16;
  undefined1 *puVar17;
  undefined4 *puVar18;
  int iVar19;
  int iVar20;
  int iVar21;
  uint uVar22;

  iVar6 = *(int *)(param_1 + 0x70);
  iVar7 = *(int *)(param_1 + 0x1cc);
  iVar8 = *(int *)(param_1 + 0x148);
  iVar9 = *(int *)(iVar7 + 8);
  iVar10 = *(int *)(iVar7 + 0xc);
  iVar11 = *(int *)(iVar7 + 0x10);
  iVar7 = *(int *)(iVar7 + 0x14);
  if (-1 < param_5 + -1) {
    iVar12 = *(int *)((int)param_2 + 4);
    iVar13 = *(int *)((int)param_2 + 8);
    iVar14 = *(int *)param_2;
    iVar15 = *(int *)((int)param_2 + 0xc);
    puVar18 = (undefined4 *)(iVar12 + param_3 * 4);
    do {
      piVar1 = (int *)((iVar14 - iVar12) + (int)puVar18);
      piVar2 = (int *)((iVar15 - iVar12) + (int)puVar18);
      pbVar16 = (byte *)*puVar18;
      piVar3 = (int *)((int)puVar18 + (iVar13 - iVar12));
      puVar17 = *(undefined1 **)param_4;
      param_4 = (void *)((int)param_4 + 4);
      puVar18 = puVar18 + 1;
      if (iVar6 != 0) {
        iVar19 = *piVar1 - (int)pbVar16;
        iVar20 = *piVar3 - (int)pbVar16;
        iVar21 = *piVar2 - (int)pbVar16;
        param_1 = iVar6;
        do {
          uVar22 = (uint)pbVar16[iVar19];
          bVar4 = pbVar16[iVar20];
          bVar5 = *pbVar16;
          *puVar17 = *(undefined1 *)(((iVar8 - *(int *)(iVar9 + (uint)bVar4 * 4)) - uVar22) + 0xff);
          puVar17[1] = *(undefined1 *)
                        (((iVar8 - (*(int *)(iVar7 + (uint)bVar5 * 4) +
                                    *(int *)(iVar11 + (uint)bVar4 * 4) >> 0x10)) - uVar22) + 0xff);
          puVar17[2] = *(undefined1 *)
                        (((iVar8 - *(int *)(iVar10 + (uint)bVar5 * 4)) - uVar22) + 0xff);
          puVar17[3] = pbVar16[iVar21];
          pbVar16 = pbVar16 + 1;
          param_1 = param_1 + -1;
          puVar17 = puVar17 + 4;
        } while (param_1 != 0);
      }
      param_5 = param_5 + -1;
    } while (param_5 != 0);
  }
  return;
}
