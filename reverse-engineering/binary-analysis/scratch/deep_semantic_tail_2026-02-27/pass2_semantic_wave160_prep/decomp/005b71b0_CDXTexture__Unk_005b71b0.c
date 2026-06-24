/* address: 0x005b71b0 */
/* name: CDXTexture__Unk_005b71b0 */
/* signature: void __stdcall CDXTexture__Unk_005b71b0(int param_1, void * param_2, void * param_3, int param_4, int param_5) */


void CDXTexture__Unk_005b71b0(int param_1,void *param_2,void *param_3,int param_4,int param_5)

{
  byte *pbVar1;
  byte *pbVar2;
  byte bVar3;
  uint uVar4;
  int iVar5;
  int iVar6;
  byte *pbVar7;
  uint uVar8;
  int *piVar9;

  uVar4 = *(uint *)(param_1 + 0x1c);
  iVar5 = *(int *)(*(int *)(param_1 + 0x168) + 8);
  if (-1 < param_5 + -1) {
    piVar9 = (int *)(*(int *)param_3 + param_4 * 4);
    param_1 = param_5;
    do {
      pbVar7 = *(byte **)param_2;
      param_2 = (void *)((int)param_2 + 4);
      iVar6 = *piVar9;
      piVar9 = piVar9 + 1;
      uVar8 = 0;
      if (uVar4 != 0) {
        do {
          pbVar1 = pbVar7 + 1;
          pbVar2 = pbVar7 + 2;
          bVar3 = *pbVar7;
          pbVar7 = pbVar7 + 3;
          *(char *)(uVar8 + iVar6) =
               (char)((uint)(*(int *)(iVar5 + 0x800 + (uint)*pbVar2 * 4) +
                             *(int *)(iVar5 + 0x400 + (uint)*pbVar1 * 4) +
                            *(int *)(iVar5 + (uint)bVar3 * 4)) >> 0x10);
          uVar8 = uVar8 + 1;
        } while (uVar8 < uVar4);
      }
      param_1 = param_1 + -1;
    } while (param_1 != 0);
  }
  return;
}
