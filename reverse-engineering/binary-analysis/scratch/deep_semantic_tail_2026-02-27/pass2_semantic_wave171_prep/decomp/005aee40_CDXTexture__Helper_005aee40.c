/* address: 0x005aee40 */
/* name: CDXTexture__Helper_005aee40 */
/* signature: void __stdcall CDXTexture__Helper_005aee40(void * param_1, int param_2, void * param_3) */


void CDXTexture__Helper_005aee40(void *param_1,int param_2,void *param_3)

{
  int iVar1;
  int iVar2;
  int iVar3;
  undefined1 *puVar4;
  int *in_EAX;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  byte *pbVar9;
  byte *pbVar10;
  int iVar11;
  byte *local_10;

  iVar1 = *in_EAX;
  iVar2 = *(int *)((int)param_1 + 0x13c);
  iVar7 = 0;
  if (0 < iVar2) {
    iVar3 = *(int *)(param_2 + 0x28);
    local_10 = *(byte **)param_3;
    param_1 = param_3;
    param_2 = 0;
    while( true ) {
      do {
        if (param_2 == 0) {
          pbVar10 = *(byte **)((int)param_1 + -4);
        }
        else {
          pbVar10 = *(byte **)((int)param_1 + 4);
        }
        puVar4 = *(undefined1 **)(iVar1 + iVar7 * 4);
        iVar7 = iVar7 + 1;
        iVar11 = (uint)*local_10 * 3 + (uint)*pbVar10;
        iVar5 = (uint)local_10[1] * 3 + (uint)pbVar10[1];
        *puVar4 = (char)(iVar11 * 4 + 8 >> 4);
        pbVar10 = pbVar10 + 2;
        pbVar9 = local_10 + 2;
        puVar4[1] = (char)(iVar11 * 3 + 7 + iVar5 >> 4);
        for (iVar8 = iVar3 + -2; puVar4 = puVar4 + 2, iVar8 != 0; iVar8 = iVar8 + -1) {
          iVar6 = (uint)*pbVar9 * 3 + (uint)*pbVar10;
          pbVar10 = pbVar10 + 1;
          *puVar4 = (char)(iVar5 * 3 + 8 + iVar11 >> 4);
          pbVar9 = pbVar9 + 1;
          puVar4[1] = (char)(iVar5 * 3 + 7 + iVar6 >> 4);
          iVar11 = iVar5;
          iVar5 = iVar6;
        }
        *puVar4 = (char)(iVar5 * 3 + 8 + iVar11 >> 4);
        puVar4[1] = (char)(iVar5 * 4 + 7 >> 4);
        param_2 = param_2 + 1;
      } while (param_2 < 2);
      param_1 = (void *)((int)param_1 + 4);
      if (iVar2 <= iVar7) break;
      local_10 = *(byte **)param_1;
      param_2 = 0;
    }
  }
  return;
}
