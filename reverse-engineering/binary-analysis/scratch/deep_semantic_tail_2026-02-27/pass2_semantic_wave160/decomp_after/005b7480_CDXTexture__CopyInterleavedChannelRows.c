/* address: 0x005b7480 */
/* name: CDXTexture__CopyInterleavedChannelRows */
/* signature: void __stdcall CDXTexture__CopyInterleavedChannelRows(int param_1, void * param_2, void * param_3, int param_4, int param_5) */


void CDXTexture__CopyInterleavedChannelRows
               (int param_1,void *param_2,void *param_3,int param_4,int param_5)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  undefined1 *puVar5;
  int *piVar6;

  uVar1 = *(uint *)(param_1 + 0x1c);
  iVar2 = *(int *)(param_1 + 0x24);
  if (-1 < param_5 + -1) {
    piVar6 = (int *)(*(int *)param_3 + param_4 * 4);
    param_1 = param_5;
    do {
      puVar5 = *(undefined1 **)param_2;
      iVar3 = *piVar6;
      param_2 = (void *)((int)param_2 + 4);
      piVar6 = piVar6 + 1;
      uVar4 = 0;
      if (uVar1 != 0) {
        do {
          *(undefined1 *)(uVar4 + iVar3) = *puVar5;
          puVar5 = puVar5 + iVar2;
          uVar4 = uVar4 + 1;
        } while (uVar4 < uVar1);
      }
      param_1 = param_1 + -1;
    } while (param_1 != 0);
  }
  return;
}
