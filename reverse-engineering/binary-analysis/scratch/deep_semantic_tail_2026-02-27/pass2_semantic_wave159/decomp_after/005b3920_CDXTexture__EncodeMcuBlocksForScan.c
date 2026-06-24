/* address: 0x005b3920 */
/* name: CDXTexture__EncodeMcuBlocksForScan */
/* signature: int __stdcall CDXTexture__EncodeMcuBlocksForScan(void * param_1, int param_2) */


int CDXTexture__EncodeMcuBlocksForScan(void *param_1,int param_2)

{
  int iVar1;
  int iVar2;
  void *pvVar3;
  int iVar4;
  void *unaff_EBX;
  undefined4 *puVar5;
  int iVar6;

  pvVar3 = param_1;
  iVar6 = *(int *)((int)param_1 + 200);
  iVar1 = *(int *)((int)param_1 + 0x174);
  if (iVar6 != 0) {
    if (*(int *)(iVar1 + 0x24) == 0) {
      iVar4 = *(int *)((int)param_1 + 0xfc);
      if (0 < iVar4) {
        puVar5 = (undefined4 *)(iVar1 + 0x14);
        for (; iVar4 != 0; iVar4 = iVar4 + -1) {
          *puVar5 = 0;
          puVar5 = puVar5 + 1;
        }
      }
      *(int *)(iVar1 + 0x24) = iVar6;
    }
    *(int *)(iVar1 + 0x24) = *(int *)(iVar1 + 0x24) + -1;
  }
  iVar6 = 0;
  if (0 < *(int *)((int)param_1 + 0x118)) {
    param_1 = (void *)((int)param_1 + 0x11c);
    do {
      iVar4 = *(int *)param_1;
      CTexture__Helper_005b3840
                (*(void **)(iVar1 + 0x14 + iVar4 * 4),(int)pvVar3,*(void **)(param_2 + iVar6 * 4),
                 *(void **)(iVar1 + 0x5c +
                           *(int *)(*(int *)((int)pvVar3 + iVar4 * 4 + 0x100) + 0x18) * 4),unaff_EBX
                );
      iVar2 = *(int *)((int)pvVar3 + 0x118);
      *(int *)(iVar1 + 0x14 + iVar4 * 4) = (int)**(short **)(param_2 + iVar6 * 4);
      iVar6 = iVar6 + 1;
      param_1 = (void *)((int)param_1 + 4);
    } while (iVar6 < iVar2);
  }
  return 1;
}
